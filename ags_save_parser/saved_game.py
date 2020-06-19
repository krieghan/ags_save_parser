import pickle

from ags_save_parser import cursor as cursor_module


MAX_ROOMS = 300
MAX_FLAGS = 15
MAX_INIT_SPR = 40
MAX_HOTSPOTS = 50
MAX_NEWINTERACTION_EVENTS = 30
MAX_REGIONS = 16
MAX_OBJ = 16
MAX_GLOBAL_VARIABLES = 100
MAXGLOBALVARS = 50
MAXGSVALUES = 500
GAME_STATE_RESERVED_INTS = 6
MAX_WALK_AREAS = 15
MAX_TIMERS = 21
MAX_PARSED_WORDS = 15
MAX_BSCENE = 5
MAXSAVEGAMES = 50
MAX_QUEUED_MUSIC = 10
PLAYMP3FILE_MAX_FILENAME_LEN = 50
MAXGLOBALSTRINGS = 51
MAX_MAXSTRLEN = 200
MAX_AUDIO_TYPES = 30
MAXGLOBALMES = 500
MAXNEEDSTAGES = 40
OPT_HIGHESTOPTION_321 = 39
MAX_INV = 301
MAX_SCRIPT_NAME_LEN = 20
MAX_INVORDER = 500
MAXTOPICOPTIONS = 30
MAX_OBJS_ON_GUI = 30
MAX_GUIOBJ_SCRIPTNAME_LEN = 25
MAX_SOUND_CHANNELS = 8
MAX_DYNAMIC_SURFACES = 20
BASEGOBJ_SIZE = 7
GALIGN_LEFT = 0

INT_BYTES = 4
COLOR_BYTES = 4

INV_SCRIPTS_NONE = False
GUIMAGIC_INT = 0xcafebeef
MAGICNUMBER = 0xbeefcafe
OBJECT_CACHE_MAGIC_NUMBER = 0xa30b
LOADED_GAME_FILE_VERSION = 300
GLF_SGINDEXVALID = 4


NOTIMPLEMENTED = 'NOTIMPLEMENTED'


KGUIVERSION_INITIAL = 0
KGUIVERSION_214 = 100
KGUIVERSION_222 = 101
KGUIVERSION_230 = 102
KGUIVERSION_UNKN_103 = 103
KGUIVERSION_UNKN_104  = 104
KGUIVERSION_260 = 105
KGUIVERSION_UNKN_106 = 106
KGUIVERSION_UNKN_107 = 107
KGUIVERSION_UNKN_108 = 108
KGUIVERSION_UNKN_109 = 109
KGUIVERSION_270 = 110
KGUIVERSION_272A = 111
KGUIVERSION_272B = 112
KGUIVERSION_272C = 113
KGUIVERSION_272D = 114
KGUIVERSION_272E = 115
KGUIVERSION_330 = 116
KGUIVERSION_CURRENT = KGUIVERSION_330
KGUIVERSION_FORWARDCOMPATIBLE = KGUIVERSION_272E


def get_save_game(filename, num_characters=None):

    with open(filename, 'rb') as save_file:
        content_bytes = save_file.read()


    cursor = cursor_module.Cursor(content_bytes, index=0)
    save_game = {}
    save_game['vista_header'] = read_vista_header(cursor)
    save_game['game_header'] = read_game_header(cursor)
    save_game['game_head_dynamic_values'] = read_game_head_dynamic_values(cursor)
    save_game['spriteset'] = read_game_spriteset(cursor)
    save_game['scripts'] = read_game_scripts(cursor)

    save_game['current_room'] = cursor.read_int(4)

    save_game['rooms'] = read_room_states(cursor)
    game_state = save_game['game_state'] = read_game_state(cursor)
    if game_state['num_do_once_tokens'] > 0:
        raise NotImplementedError('do once token logic not implemented')
    guess_numgui = save_game['guess_numgui'] = get_numgui(cursor)
    save_game['gui_draw_order'] = cursor.read_array_of_ints(
        element_size=4,
        array_size=guess_numgui)

    if num_characters is None:
        guessing_num_characters = True
        (move_lists, total_runs, align_cursor) =\
            read_move_lists(cursor)

        # Make sure we rewind the cursor to ignore the failed run
        cursor = align_cursor.cursor
        num_characters =\
            save_game['guess_num_characters'] =\
                total_runs - MAX_INIT_SPR
        print("I'm guessing the value of num_characters should be {}".format(
            guess_num_characters))
    else:
        guessing_num_characters = False
        (move_lists, total_runs, align_cursor) =\
            read_move_lists(cursor, num_characters)

    save_game['move_lists'] = move_lists


    game_struct_base =\
        save_game['game_struct_base'] =\
            read_game_struct_base(cursor)

    '''
    if game_struct_base['numcharacters'] != num_characters:
        raise AssertionError(
            'Our guess of num_characters {} did not match what we read '
            'from the game_struct.  It is unlikely that either of these is '
            'correct.  Please provide num_characters as an argument'.format(
                num_characters,
                game_struct_base['numcharacters']))
    if game_struct_base['numgui'] != guess_numgui:
        raise AssertionError(
            'Our guess of numgui {} did not match what we read from the '
            'game struct.  It is unlikely that either of these is correct.  '
            'Please provide numgui as an argument'.format(
                guess_numgui,
                game_struct_base['numgui']))
    '''


    save_game['game_struct'] = read_game_struct(cursor, game_struct_base)
    save_game['palette'] = [x.hex() for x in cursor.read_array(
        element_size=COLOR_BYTES,
        array_size=256)]
    save_game['dialogs'] = read_dialogs(cursor, game_struct_base['numdialog'])
    save_game['more_dynamic_values'] = read_more_dynamic_values(cursor)
    save_game['gui'] = read_gui(cursor)
    save_game['audiocliptypes'] = read_audio_clip_types(cursor)
    save_game['this_room'] = read_this_room(cursor)
    save_game['ambient_sounds'] = read_ambient_sounds(cursor)
    save_game['overlays'] = read_overlays(cursor)
    save_game['dynamic_surfaces'] = read_dynamic_surfaces(cursor)
    save_game['displayed_room_status'] = read_displayed_room_status(
        cursor,
        game_state)
    save_game['global_vars'] = read_global_vars(cursor)
    save_game['game_views'] = read_game_views(cursor)
    save_game['audioclips'] = read_audioclips(cursor)
    save_game['plugin_data'] = read_plugin_data(cursor)
    save_game['this_room_volume'] = cursor.read_int(4)
    save_game['deserialized_objects'] = read_serialized_objects(cursor)
    save_game['current_music_type'] = cursor.read_int(4)
    assert cursor.index == len(cursor.content_bytes)
    return save_game

def read_game_scripts(cursor):
    scripts = {}
    global_data_size = scripts['global_data_size'] = cursor.read_int(4)
    scripts['global_data'] = cursor.read_bytes(global_data_size)
    num_script_modules = scripts['num_script_modules'] = cursor.read_int(4)

    modules = scripts['modules'] = []
    for i in range(num_script_modules):
        module_size = cursor.read_int(4)
        module = cursor.read_bytes(module_size)
        modules.append((module_size, module))
    return scripts


def read_game_spriteset(cursor):
    spriteset = {}
    spriteset['spriteset_size'] = cursor.read_int(4)
    sprite_num = cursor.read_int(4)
    sprites = spriteset['sprites'] = []
    while sprite_num > 0:
        sprite = {}
        sprites.append(sprite)
        sprite['sprite_num'] = sprite_num
        sprite['spriteflag'] = cursor.read_bytes(1)
        sprite['bmp'] = read_serialized_bitmap(cursor)
        sprite_num = cursor.read_int(4)

    return spriteset


def read_game_head_dynamic_values(cursor):
    struct = {}
    struct['screenheight'] = cursor.read_int(4)
    struct['colordepth'] = cursor.read_int(4)
    struct['gamespeed'] = cursor.read_int(4)
    struct['mode'] = cursor.read_int(4)
    struct['savecursor'] = cursor.read_int(4)
    struct['offset_x'] = cursor.read_int(4)
    struct['offset_y'] = cursor.read_int(4)
    struct['loop_counter'] = cursor.read_int(4)
    return struct


def read_game_header(cursor):
    game_header = {}
    game_header['version_string'] = cursor.read_string(200) 
    game_header['main_data_filename'] = cursor.read_string(180)
    return game_header


def read_vista_header(cursor):
    vista_header = {}
    vista_header['header_magic_string'] = cursor.read_bytes(4)
    vista_header['header_version'] = cursor.read_int(4)  
    vista_header['header_size'] = cursor.read_int(4)
    vista_header['thumbnail_offset_lower_dword'] = cursor.read_int(4)
    vista_header['thumbnail_offset_upper_dword'] = cursor.read_int(4)
    vista_header['thumbnail_size'] = cursor.read_int(4)
    vista_header['guid_game_id'] = cursor.read_bytes(16)
    vista_header['game_name'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=1024)
    vista_header['save_game_name'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=1024)
    vista_header['level_name'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=1024)
    vista_header['comments'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=1024)
    vista_header['savegame_sig'] = cursor.read_bytes(32)
    vista_header['description'] = cursor.read_string(180)
    vista_header['savegame_version'] = cursor.read_int(4)
    is_screenshot = vista_header['is_screenshot'] = cursor.read_int(4)
    if is_screenshot:
        raise NotImplementedError('No support for saved games with screenshots')
    return vista_header

def read_serialized_objects(cursor):
    struct = {}
    object_cache_magic_number = struct['magic_number'] = cursor.read_int(
        4,
        assert_value=OBJECT_CACHE_MAGIC_NUMBER)
    data_version = struct['data_version'] = cursor.read_int(4, assert_value=1)
    num_objects = struct['num_objects'] = cursor.read_int(4)
    objects = struct['objects'] = []
    for i in range(num_objects - 1):
        object_struct = {}
        objects.append(object_struct)
        type_name =\
            object_struct['type_name'] =\
                cursor.read_string(max_length=199)
        if type_name != b'':
            num_bytes = object_struct['num_bytes'] = cursor.read_int(4)
            if num_bytes > 0:
                object_struct['object_bytes'] = cursor.read_bytes(num_bytes)
            # We could unserialize these objects, but I'm not going to
            # implement that now.  Info on how is in the "Unserialize"
            # method in Engine/ac/dynobj/cc_serializer.cpp
            object_struct['ref_count'] = cursor.read_int(4)
    return struct


def read_plugin_data(cursor):
    '''I don't have access to the plugins, so I don't know what they're
       doing.  What I do know is that we match this magic number
       right after we load the plugins, so I'm going to look for that,
       and return as soon as we're done.  What I'm returning, exactly,
       is just bytes - I don't know how to interpret it.
       
       There is a possibility that the plugins write this magic number
       at some point, which would mean we're kind of screwed.  We can
       figure out some way to assert that this happens x times and
       skip them, maybe.'''

    magic_num_bytes = MAGICNUMBER.to_bytes(4, byteorder='little')
    match_index = 0
    plugin_data = []
    while True:
        new_data = cursor.read_int(1)
        plugin_data.append(new_data)
        if new_data == magic_num_bytes[match_index]:
            match_index += 1
        else:
            match_index = 0

        if match_index == 4:
            return plugin_data[0:-4]

def scan_for_value(cursor, value, size=4):
    value_bytes = value.to_bytes(4, byteorder='little')
    match_index = 0
    data = []
    while True:
        new_data = cursor.read_int(1)
        data.append(new_data)
        if new_data == value_bytes[match_index]:
            match_index += 1
        else:
            match_index = 0
        if match_index == size:
            return data



def read_audioclips(cursor):
    struct = {}
    clip_count = struct['clip_count'] = cursor.read_int(4) 
    channels = struct['channels'] = []
    for i in range(MAX_SOUND_CHANNELS):
        channel = {}
        channels.append(channel)
        channel['id'] = cursor.read_int(4, signed=True) 
        if channel['id'] < 0:
            channel['null'] = True
        else:
            channel['null'] = False
            channel['position'] = cursor.read_int(4)
            channel['priority'] = cursor.read_int(4)
            channel['repeat'] = cursor.read_int(4)
            channel['volume'] = cursor.read_int(4)
            channel['panning'] = cursor.read_int(4)
            channel['volume_as_percentage'] = cursor.read_int(4)
            channel['panning_as_percentage'] = cursor.read_int(4)
    struct['cross_fading'] = cursor.read_int(4)
    struct['cross_fade_volume_per_step'] = cursor.read_int(4)
    struct['cross_fade_step'] = cursor.read_int(4)
    struct['cross_fade_volume_at_start'] = cursor.read_int(4)
    return struct


def read_game_views(cursor):
    struct = {}
    numviews = struct['numviews'] = cursor.read_int(4)
    views_data = struct['views_data'] = []
    while True:
        new_data = cursor.read_int(4)
        if new_data == MAGICNUMBER + 1:
            break
        else:
            views_data.append(new_data)
    if numviews == 0:
        cursor.read_int(4, assert_value=MAGICNUMBER + 1)

    return struct



def read_global_vars(cursor):
    struct = {}
    num_global_vars = struct['num_global_vars'] = cursor.read_int(4)
    global_vars = struct['global_vars'] = []
    for i in range(num_global_vars):
        global_var = {}
        global_vars.append(global_var)
        global_var['name'] = cursor.read_string(
            max_length=23,
            null_terminated=False)
        global_var['type'] = cursor.read_int(1)
        global_var['value'] = cursor.read_int(4)
    return struct



def read_displayed_room_status(cursor, game_state):
    # If displayed_room >= 0
    displayed_room_state = {}
    bmps = displayed_room_state['bmps'] = []
    for i in range(MAX_BSCENE):
        if game_state['raw_modified'][i]:
            bmps.append(read_serialized_bitmap(cursor))

    raw_saved_screen =\
        displayed_room_state['raw_saved_screen'] =\
            cursor.read_int(4)
    if raw_saved_screen:
        displayed_room_state['raw_saved_bmp'] =\
            read_serialized_bitmap(cursor)

    current_room_state =\
        displayed_room_state['room_state'] =\
            read_room_state(
                cursor,
                been_here=None)
    displayed_room_state['ts_data'] =\
        cursor.read_bytes(
            length=current_room_state['ts_data_size'])
    return displayed_room_state


def read_dynamic_surfaces(cursor):
    dynamic_surfaces = []
    for i in range(MAX_DYNAMIC_SURFACES):
        surface = {}
        dynamic_surfaces.append(surface)
        surface['present'] = cursor.read_bool(1)
        if surface['present']:
            surface['bmp'] = read_serialized_bitmap(cursor) 
    return dynamic_surfaces

def read_overlays(cursor):
    overlay_struct = {}
    numscreenover = overlay_struct['numscreenover'] = cursor.read_int(4)
    align_cursor = cursor_module.AlignedCursor(cursor)
    overlays = overlay_struct['overlays'] = []
    for i in range(numscreenover):
        overlay = {}
        overlays.append(overlay)
        overlay['bmp'] = align_cursor.read_int(4, assert_value=0)
        overlay['pic'] = align_cursor.read_bool(4)
        overlay['type'] = align_cursor.read_int(4)
        overlay['x'] = align_cursor.read_int(4)
        overlay['y'] = align_cursor.read_int(4)
        overlay['timeout'] = align_cursor.read_int(4)
        overlay['bg_speech_for_char'] = align_cursor.read_int(4)
        overlay['associated_overlay_handle'] = align_cursor.read_int(4)
        overlay['has_alpha_channel'] = align_cursor.read_bool(1)
        overlay['position_relative_to_screen'] = align_cursor.read_bool(1)
        align_cursor.finalize()

    
    for i in range(numscreenover):
        overlays[i]['bmp'] = read_serialized_bitmap(cursor)
    return overlay_struct


def read_serialized_bitmap(cursor):
    bmp_struct = {}
    width = bmp_struct['width'] = cursor.read_int(4)
    height = bmp_struct['height'] = cursor.read_int(4)
    colordepth = bmp_struct['colordepth'] = cursor.read_int(4)
    bmp = bmp_struct['bmp'] = []
    for i in range(height):
        if colordepth == 8 or colordepth == 15:
            line = cursor.read_array_of_ints(
                element_size=1,
                array_size=width)
        elif colordepth == 16:
            line = cursor.read_array_of_ints(
                element_size=2,
                array_size=width)
        elif colordepth == 32:
            line = cursor.read_array_of_ints(
                element_size=4,
                array_size=width)
        else:
            raise Exception('Unknown color depth: {}'.format(colordepth))
        bmp.append(line)
    return bmp_struct

def read_ambient_sounds(cursor):
    sounds = []
    for i in range(MAX_SOUND_CHANNELS):
        sound = {}
        sounds.append(sound)
        sound['channel'] = cursor.read_int(4)
        sound['x'] = cursor.read_int(4)
        sound['y'] = cursor.read_int(4)
        sound['vol'] = cursor.read_int(4)
        sound['num'] = cursor.read_int(4)
        sound['maxdist'] = cursor.read_int(4)
    return sounds


def read_this_room(cursor):
    this_room = {}
    this_room['region_light_level'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=MAX_REGIONS)
    this_room['region_tint_level'] = cursor.read_array_of_ints(
        element_size=4,
        array_size=MAX_REGIONS)
    this_room['walk_area_zoom'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=MAX_WALK_AREAS + 1)
    this_room['walk_area_zoom_2'] = cursor.read_array_of_ints(
        element_size=2,
        array_size=MAX_WALK_AREAS + 1)
    return this_room
    

def read_audio_clip_types(cursor):
    audio_clip_types = {}
    audio_clip_type_count =\
        audio_clip_types['audio_clip_type_count'] = cursor.read_int(4)
    audio_list = audio_clip_types['list'] = []
    for i in range(audio_clip_type_count):
        audio_type = {}
        audio_list.append(audio_type)
        audio_type['id'] = cursor.read_int(4)
        audio_type['reserved_channels'] = cursor.read_int(4)
        audio_type[
            'volume_reduction_while_speech_playing'] = cursor.read_int(4)
        audio_type['crossfade_speed'] = cursor.read_int(4)
        audio_type['reserved_for_future'] = cursor.read_int(4)

    return audio_clip_types



def read_gui(cursor):
    gui_struct = {}
    guimagic = gui_struct['guimagic'] = cursor.read_int(4)
    assert guimagic == GUIMAGIC_INT
    gui_version = gui_struct['version'] = cursor.read_int(4)
    numgui = gui_struct['numgui'] = cursor.read_int(4)
    
    gui_struct['guis'] = guis = []
    for i in range(numgui):
        gui = {}
        guis.append(gui)
        gui['vtext'] = cursor.read_array_of_ints(
            element_size=1,
            array_size=40)
        gui['x'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=27)
        gui['dummyarr'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=MAX_OBJS_ON_GUI)
        gui['objectrefptr'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=MAX_OBJS_ON_GUI)
    numguibuts = gui_struct['numguibuts'] = cursor.read_int(4)
    gui_struct['buttons'] = buttons = []

    for i in range(numguibuts):
        button = {}
        buttons.append(button)
        button['base'] = get_base_gui_object(cursor, gui_version)
        button['pic'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=12)
        button['text'] = cursor.read_string_from_array_of_ints(
            element_size=1,
            array_size=50)
        button['text_alignment'] = cursor.read_int(4)
        button['reserved1'] = cursor.read_int(4)
    numguilabels = gui_struct['numguilabels'] = cursor.read_int(4)
    labels = gui_struct['labels'] = []
    for i in range(numguilabels):
        label = {}
        labels.append(label)
        label['base'] = get_base_gui_object(cursor, gui_version)
        label['text_length'] = cursor.read_int(4)
        label['text'] = cursor.read_string(
            max_length=label['text_length'],
            null_terminated=False)
        label['font'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=3)
    numguiinv = gui_struct['numguiinv'] = cursor.read_int(4)
    invs = gui_struct['inv'] = []
    for i in range(numguiinv):
        inv = {}
        invs.append(inv)
        inv['base'] = get_base_gui_object(cursor, gui_version)
        if gui_version >= KGUIVERSION_UNKN_109:
            inv['char_id'] = cursor.read_int(4)
            inv['item_width'] = cursor.read_int(4)
            inv['item_height'] = cursor.read_int(4)
            inv['top_index'] = cursor.read_int(4)
        else:
            inv['char_id'] = -1
            inv['item_width'] = 40
            inv['item_height'] = 22
            inv['top_index'] = 0
    numguislider = gui_struct['numguislider'] = cursor.read_int(4)
    sliders = gui_struct['sliders'] = []
    for i in range(numguislider):
        slider = {}
        sliders.append(slider)
        slider['base'] = get_base_gui_object(cursor, gui_version)
        if gui_version > KGUIVERSION_UNKN_104:
            size_to_read = 7
        else:
            size_to_read = 4
        slider['min'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=size_to_read)
    numguitext = gui_struct['numguitext'] = cursor.read_int(4)
    text_boxes = gui_struct['text_boxes'] = []
    for i in range(numguitext):
        text_box = {}
        text_boxes.append(text_box)
        text_box['base'] = get_base_gui_object(cursor, gui_version)
        text_box['text'] = cursor.read_string(
            max_length=200,
            null_terminated=False)
        text_box['font'] = cursor.read_array_of_ints(
            element_size=4,
            array_size=3)
    numguilist = gui_struct['numguilist'] = cursor.read_int(4)
    gui_lists = gui_struct['lists'] = []
    for i in range(numguilist):
        gui_list = {}
        gui_lists.append(gui_list)
        gui_list['base'] = get_base_gui_object(cursor, gui_version)
        (gui_list['num_items'], 
         gui_list['selected'],
         gui_list['topItem'],
         gui_list['mousexp'],
         gui_list['mouseyp'],
         gui_list['rowheight'],
         gui_list['num_items_fit'],
         gui_list['font'],
         gui_list['textcol'],
         gui_list['backcol'],
         gui_list['exflags']) = cursor.read_array_of_ints(
            element_size=4,
            array_size=11)

        num_items = gui_list['num_items']

        if gui_version >= KGUIVERSION_272B:
            gui_list['alignment'] = cursor.read_int(4)
            gui_list['reserved1'] = cursor.read_int(4)
        else:
            gui_list['alignment'] = GALIGN_LEFT
            gui_list['reserved1'] = 0

        if gui_version >= KGUIVERSION_UNKN_107:
            gui_list['selectedbgcol'] = cursor.read_int(4)
        else:
            gui_list['selectedbgcol'] = NOTIMPLEMENTED 

        items = gui_list['items'] = []
        for j in range(num_items):
            new_item = cursor.read_string(max_length=None)
            items.append(new_item)
        if (gui_version >= KGUIVERSION_272D and 
                gui_list['exflags'] & GLF_SGINDEXVALID):
            gui_list['savegameindex'] = cursor.read_array_of_ints(
                element_size=2,
                array_size=num_items)
    num_anim_buttons = gui_struct['num_anim_buttons'] = cursor.read_int(4)
    align_cursor = cursor_module.AlignedCursor(cursor)
    animated_buttons = gui_struct['animated_buttons'] = []
    for i in range(num_anim_buttons):
        animated_button = {}
        animated_buttons.append(animated_button)
        animated_button['buttonid'] = align_cursor.read_int(2)
        animated_button['ongui'] = align_cursor.read_int(2)
        animated_button['onguibut'] = align_cursor.read_int(2)
        animated_button['view'] = align_cursor.read_int(2)
        animated_button['loop'] = align_cursor.read_int(2)
        animated_button['frame'] = align_cursor.read_int(2)
        animated_button['speed'] = align_cursor.read_int(2)
        animated_button['repeat'] = align_cursor.read_int(2)
        animated_button['wait'] = align_cursor.read_int(2)
        align_cursor.finalize()
    return gui_struct


def get_base_gui_object(cursor, gui_version):
    base = {}
    base['flags'] = cursor.read_array_of_ints(
        element_size=4,
        array_size=BASEGOBJ_SIZE)
    if gui_version > 106:
        base['script_name'] = cursor.read_string(
            max_length=MAX_GUIOBJ_SCRIPTNAME_LEN)
    else:
        base['script_name'] = ''

    if gui_version >= 108:
        num_events = base['num_events'] = cursor.read_int(4)
        events = base['events'] = []
        for j in range(num_events):
            events.append(cursor.read_string())
    return base


def read_dialogs(cursor, numdialogs):
    dialogs = []
    for i in range(numdialogs):
        dialogs.append(
            cursor.read_array_of_ints(
                element_size=4,
                array_size=MAXTOPICOPTIONS))
    return dialogs

def read_more_dynamic_values(cursor):
    more_dynamic_values = {}
    more_dynamic_values['mouse_on_iface'] = cursor.read_int(4)
    more_dynamic_values['mouse_on_iface_button'] = cursor.read_int(4)
    more_dynamic_values['mouse_pushed_iface'] = cursor.read_int(4)
    more_dynamic_values['ifacepopped'] = cursor.read_int(4)
    more_dynamic_values['game_paused'] = cursor.read_int(4)
    return more_dynamic_values
        

def read_game_struct(cursor, game_struct_base):
    game_struct = {}
    numinvitems = game_struct_base['numinvitems']
    numcursors = game_struct_base['numcursors']
    numcharacters = game_struct_base['numcharacters']
    game_struct['inv_items'] = read_inv_items(cursor, numinvitems)
    game_struct['mouse_cursors'] = read_mouse_cursors(cursor, numcursors)

    if INV_SCRIPTS_NONE:
        game_struct['inv_intr_times_run'] = inv_intr_times_run = []
        game_struct['char_intr_times_run'] = char_intr_times_run = []
        for i in range(numinvitems):
            inv_intr_times_run.append(
                cursor.read_array_of_ints(
                    element_size=4,
                    array_size=MAX_NEWINTERACTION_EVENTS))
        for i in range(numcharacters):
            char_intr_times_run.append(
                cursor.read_array_of_ints(
                    element_size=4,
                    array_size=MAX_NEWINTERACTION_EVENTS))
    else:
        game_struct['inv_intr_times_run'] = None
        game_struct['char_intr_times_run'] = None

    game_struct['options'] = cursor.read_array_of_ints(
        element_size=4,
        array_size=OPT_HIGHESTOPTION_321 + 1)
    game_struct['option_lipsynctext'] = cursor.read_int(1)
    game_struct['characters'] = read_characters(cursor, numcharacters)
    return game_struct


def read_characters(cursor, numcharacters):
    align_cursor = cursor_module.AlignedCursor(cursor)
    characters = []
    for i in range(numcharacters):
        character = {}
        characters.append(character)
        character['defview'] = align_cursor.read_int(4)
        character['talkview'] = align_cursor.read_int(4)
        character['view'] = align_cursor.read_int(4)
        character['room'] = align_cursor.read_int(4)
        character['prevroom'] = align_cursor.read_int(4)
        character['x'] = align_cursor.read_int(4)
        character['y'] = align_cursor.read_int(4)
        character['wait'] = align_cursor.read_int(4)
        character['flags'] = align_cursor.read_int(4)
        character['following'] = align_cursor.read_int(2)
        character['followinfo'] = align_cursor.read_int(2)
        character['idleview'] = align_cursor.read_int(4)
        character['idletime'] = align_cursor.read_int(2)
        character['idleleft'] = align_cursor.read_int(2)
        character['transparency'] = align_cursor.read_int(2)
        character['baseline'] = align_cursor.read_int(2)
        character['activeinv'] = align_cursor.read_int(4)
        character['talkcolor'] = align_cursor.read_int(4)
        character['thinkview'] = align_cursor.read_int(4)
        character['blinkview'] = align_cursor.read_int(2)
        character['blinkinterval'] = align_cursor.read_int(2)
        character['blinktimer'] = align_cursor.read_int(2)
        character['blinkframe'] = align_cursor.read_int(2)
        character['walkspeed_y'] = align_cursor.read_int(2)
        character['pic_yoffs'] = align_cursor.read_int(2)
        character['z'] = align_cursor.read_int(4)
        character['walkwait'] = align_cursor.read_int(4)
        character['speech_anim_speed'] = align_cursor.read_int(2)
        character['reserved1'] = align_cursor.read_int(2)
        character['blocking_width'] = align_cursor.read_int(2)
        character['blocking_height'] = align_cursor.read_int(2)
        character['index_id'] = align_cursor.read_int(4)
        character['pic_xoffs'] = align_cursor.read_int(2)
        character['walkwaitcounter'] = align_cursor.read_int(2)
        character['loop'] = align_cursor.read_int(2)
        character['frame'] = align_cursor.read_int(2)
        character['walking'] = align_cursor.read_int(2)
        character['animating'] = align_cursor.read_int(2)
        character['walkspeed'] = align_cursor.read_int(2)
        character['animspeed'] = align_cursor.read_int(2)
        character['inv'] = align_cursor.read_array_of_ints(
                element_size=2,
                array_size=MAX_INV)
        character['actx'] = align_cursor.read_int(2)
        character['acty'] = align_cursor.read_int(2)
        character['name'] = align_cursor.read_string_from_array_of_ints(
                element_size=1,
                array_size=40)
        character['scrname'] = align_cursor.read_string_from_array_of_ints(
                element_size=1,
                array_size=MAX_SCRIPT_NAME_LEN)
        character['on'] = align_cursor.read_int(1)
        character['extra'] = {}
        align_cursor.finalize()

    for i in range(numcharacters):
        characters[i]['extra'] = extra = {}
        extra['invorder'] = align_cursor.read_array_of_ints(
            element_size=2,
            array_size=MAX_INVORDER)
        extra['invorder_count'] = align_cursor.read_int(2)
        extra['width'] = align_cursor.read_int(2)
        extra['height'] = align_cursor.read_int(2)
        extra['zoom'] = align_cursor.read_int(2)
        extra['xwas'] = align_cursor.read_int(2)
        extra['ywas'] = align_cursor.read_int(2)
        extra['tint_r'] = align_cursor.read_int(2)
        extra['tint_g'] = align_cursor.read_int(2)
        extra['tint_b'] = align_cursor.read_int(2)
        extra['tint_level'] = align_cursor.read_int(2)
        extra['tint_light'] = align_cursor.read_int(2)
        extra['process_idle_this_time'] = align_cursor.read_int(1)
        extra['slow_move_counter'] = align_cursor.read_int(1)
        extra['animwait'] = align_cursor.read_int(2)
        align_cursor.finalize()

    
    return characters

def read_inv_items(cursor, numinvitems):
    align_cursor = cursor_module.AlignedCursor(cursor)
    inv_items = []
    for i in range(numinvitems):
        inv_item = {}
        inv_items.append(inv_item)
        inv_item['name'] = align_cursor.read_array_of_ints(
            element_size=1,
            array_size=25)
        inv_item['pic'] = align_cursor.read_int(4)
        inv_item['cursorPic'] = align_cursor.read_int(4)
        inv_item['hotx'] = align_cursor.read_int(4)
        inv_item['hoty'] = align_cursor.read_int(4)
        inv_item['reserved'] = align_cursor.read_array_of_ints(
            element_size=4,
            array_size=5)
        inv_item['flags'] = align_cursor.read_int(1)
        align_cursor.finalize()
    return inv_items


def read_mouse_cursors(cursor, numcursors):
    align_cursor = cursor_module.AlignedCursor(cursor)
    mouse_cursors = []
    for i in range(numcursors):
        mouse_cursor = {}
        mouse_cursors.append(mouse_cursor)
        mouse_cursor['pic'] = align_cursor.read_int(4)
        mouse_cursor['hotx'] = align_cursor.read_int(2)
        mouse_cursor['hoty'] = align_cursor.read_int(2)
        mouse_cursor['view'] = align_cursor.read_int(2)
        mouse_cursor['name'] = align_cursor.read_array_of_ints(
            element_size=1,
            array_size=10)
        mouse_cursor['flags'] = align_cursor.read_int(1)
        align_cursor.finalize()
    return mouse_cursors


def read_game_struct_base(cursor):
    align_cursor = cursor_module.AlignedCursor(cursor)
    game_struct = {}
    game_struct['game_name'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=50)
    game_struct['options'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=100)
    game_struct['paluses'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=256)
    game_struct['defpal'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=COLOR_BYTES * 256)
    game_struct['numviews'] = align_cursor.read_int(4)
    game_struct['numcharacters'] = align_cursor.read_int(4)
    game_struct['playercharacter'] = align_cursor.read_int(4)
    game_struct['totalscore'] = align_cursor.read_int(4)
    game_struct['numinvitems'] = align_cursor.read_int(2)
    game_struct['numdialog'] = align_cursor.read_int(4)
    game_struct['numdlgmessage'] = align_cursor.read_int(4)
    game_struct['numfonts'] = align_cursor.read_int(4)
    game_struct['color_depth'] = align_cursor.read_int(4)
    game_struct['target_win'] = align_cursor.read_int(4)
    game_struct['dialog_bullet'] = align_cursor.read_int(4)
    game_struct['hotdot'] = align_cursor.read_int(2)
    game_struct['hotdotouter'] = align_cursor.read_int(2)
    game_struct['uniqueid'] = align_cursor.read_int(4)
    game_struct['numgui'] = align_cursor.read_int(4)
    game_struct['numcursors'] = align_cursor.read_int(4)
    game_struct['default_resolution'] = align_cursor.read_int(4)
    game_struct['default_lipsync_frame'] = align_cursor.read_int(4)
    game_struct['invhotdotsprite'] = align_cursor.read_int(4)
    game_struct['reserved'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=17)
    game_struct['messages'] = []
    for i in range(MAXGLOBALMES):
        game_struct['messages'].append(
            align_cursor.read_bool(4))
    game_struct['dict'] = align_cursor.read_bool(4)
    game_struct['globalscript'] = align_cursor.read_int(4, assert_value=0)
    game_struct['chars'] = align_cursor.read_int(4, assert_value=0)
    game_struct['compiled_script'] = align_cursor.read_int(4, assert_value=0)
    align_cursor.finalize()
    return game_struct


def save_cursor_state(cursor):
    return pickle.dumps(cursor)


def load_cursor_state(save_point):
    cursor = pickle.loads(save_point)
    return cursor
    

def read_move_lists(cursor, num_characters=None):
    '''The trick here is there are (MAX_INIT_SPR + num_characters) 
       move_lists to read, but we don't know the value of num_characters
       until later in the file.  Read until we fail.  When we fail,
       restore the cursor to its state before the failed run.  Return
       num_characters along with the move_lists themselves,
       and later on when we read the real num_characters out of the file,
       we'll check to see if they match.  If they don't, we either bailed
       too early (because of a spurious exception, probably) or we read
       further than we should have (because we didn't get an exception
       on the first false run).  Obviously, none of this is ideal'''

    align_cursor = cursor_module.AlignedCursor(cursor)
    move_lists = []

    if num_characters is None:
        i = 0
        while True:
            save_point = save_cursor_state(align_cursor)
            try:
                move_list = read_move_list(align_cursor, guessing=True)
            except Exception as e:
                print(e)
                if i < MAX_INIT_SPR:
                    # We shouldn't fail in the first MAX_INIT_SPR runs.  If we do
                    # it's a real exception and we should reraise it.
                    raise
                align_cursor = load_cursor_state(save_point)
                break
            else:
                align_cursor.finalize()
                move_lists.append(move_list)
            i += 1
    else:
        for i in range(num_characters + MAX_INIT_SPR):
            move_lists.append(read_move_list(align_cursor, guessing=False))
            align_cursor.finalize()
    return (
        move_lists,
        i,
        align_cursor)



def read_move_list(align_cursor, guessing=True):
    move_list = {}
    move_list['pos'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=MAXNEEDSTAGES)
    move_list['numstage'] = align_cursor.read_int(4)
    move_list['xpermove'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=MAXNEEDSTAGES)
    move_list['ypermove'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=MAXNEEDSTAGES)
    move_list['fromx'] = align_cursor.read_int(4)
    move_list['fromy'] = align_cursor.read_int(4)
    move_list['onstage'] = align_cursor.read_int(4)
    move_list['onpart'] = align_cursor.read_int(4)
    move_list['lastx'] = align_cursor.read_int(4)
    move_list['lasty'] = align_cursor.read_int(4)
    if guessing:
        move_list['doneflag'] = align_cursor.read_bool(1)
    else:
        move_list['doneflag'] = align_cursor.read_int(1)
    move_list['direct'] = align_cursor.read_int(1)
    return move_list



def get_numgui(cursor):
    # I know its 50 for Heroines Quest - it might be different for others?
    # TODO: Make this a dynamic guess.  Get the sorted list, and increase
    # the size until we've got them all
    return 50
    

def read_game_state(cursor):
    game_state = {}
    align_cursor = cursor_module.AlignedCursor(cursor)
    game_state['score'] = align_cursor.read_int(4)
    game_state['usedmode'] = align_cursor.read_int(4)
    game_state['disabled_user_interface'] = align_cursor.read_int(4)
    game_state['gscript_timer'] = align_cursor.read_int(4)
    game_state['debug_mode'] = align_cursor.read_int(4)
    game_state['global_vars'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=MAXGLOBALVARS)
    game_state['message_time'] = align_cursor.read_int(4)
    game_state['usedinv'] = align_cursor.read_int(4)
    game_state['inv_top'] = align_cursor.read_int(4)
    game_state['inv_numdisp'] = align_cursor.read_int(4)
    game_state['obsolete_inv_numorder'] = align_cursor.read_int(4)
    game_state['inv_numinline'] = align_cursor.read_int(4)
    game_state['text_speed'] = align_cursor.read_int(4)
    game_state['sierra_inv_color'] = align_cursor.read_int(4)
    game_state['talkanim_speed'] = align_cursor.read_int(4)
    game_state['inv_item_wid'] = align_cursor.read_int(4)
    game_state['inv_item_hit'] = align_cursor.read_int(4)
    game_state['speech_text_shadow'] = align_cursor.read_int(4)
    game_state['swap_portait_side'] = align_cursor.read_int(4)
    game_state['speech_textwindow_gui'] = align_cursor.read_int(4)
    game_state['follow_change_room_timer'] = align_cursor.read_int(4)
    game_state['totalscore'] = align_cursor.read_int(4)
    game_state['skip_display'] = align_cursor.read_int(4)
    game_state['no_multiloop_repeat'] = align_cursor.read_int(4)
    game_state['roomscript_finished'] = align_cursor.read_int(4)
    game_state['used_inv_on'] = align_cursor.read_int(4)
    game_state['no_textbg_when_voice'] = align_cursor.read_int(4)
    game_state['max_dialogoption_width'] = align_cursor.read_int(4)
    game_state['no_hicolor_fadein'] = align_cursor.read_int(4)
    game_state['bgspeech_game_speed'] = align_cursor.read_int(4)
    game_state['bgspeech_stay_on_display'] = align_cursor.read_int(4)
    game_state['unfactor_speech_from_textlength'] = align_cursor.read_int(4)
    game_state['mp3_loop_before_end'] = align_cursor.read_int(4)
    game_state['speech_music_drop'] = align_cursor.read_int(4)
    game_state['in_cutscene'] = align_cursor.read_int(4)
    game_state['fast_forward'] = align_cursor.read_int(4)
    game_state['room_width'] = align_cursor.read_int(4)
    game_state['room_height'] = align_cursor.read_int(4)
    game_state['game_speed_modifier'] = align_cursor.read_int(4)
    game_state['score_sound'] = align_cursor.read_int(4)
    game_state['takeover_data'] = align_cursor.read_int(4)
    game_state['replay_hotkey'] = align_cursor.read_int(4)
    game_state['dialog_options_x'] = align_cursor.read_int(4)
    game_state['dialog_options_y'] = align_cursor.read_int(4)
    game_state['narrator_speech'] = align_cursor.read_int(4)
    game_state['ambient_sounds_persist'] = align_cursor.read_int(4)
    game_state['lipsync_speed'] = align_cursor.read_int(4)
    game_state['close_mouth_speech_time'] = align_cursor.read_int(4)
    game_state['disable_antialiasing'] = align_cursor.read_int(4)
    game_state['text_speed_modifier'] = align_cursor.read_int(4)
    game_state['text_align'] = align_cursor.read_int(4)
    game_state['speech_bubble_width'] = align_cursor.read_int(4)
    game_state['min_dialogoption_width'] = align_cursor.read_int(4)
    game_state['disable_dialog_parser'] = align_cursor.read_int(4)
    game_state['anim_background_speed'] = align_cursor.read_int(4)
    game_state['top_bar_backcolor'] = align_cursor.read_int(4)
    game_state['top_bar_textcolor'] = align_cursor.read_int(4)
    game_state['top_bar_bordercolor'] = align_cursor.read_int(4)
    game_state['top_bar_borderwidth'] = align_cursor.read_int(4)
    game_state['top_bar_ypos'] = align_cursor.read_int(4)
    game_state['screenshot_width'] = align_cursor.read_int(4)
    game_state['screenshot_height'] = align_cursor.read_int(4)
    game_state['top_bar_front'] = align_cursor.read_int(4)
    game_state['speech_text_align'] = align_cursor.read_int(4)
    game_state['auto_use_walkto_points'] = align_cursor.read_int(4)
    game_state['inventory_greys_out'] = align_cursor.read_int(4)
    game_state['skip_speech_specific_key'] = align_cursor.read_int(4)
    game_state['abort_key'] = align_cursor.read_int(4)
    game_state['fade_to_red'] = align_cursor.read_int(4)
    game_state['fade_to_green'] = align_cursor.read_int(4)
    game_state['fade_to_blue'] = align_cursor.read_int(4)
    game_state['show_single_dialog_option'] = align_cursor.read_int(4)
    game_state['keep_screen_during_instant_transition'] =\
        align_cursor.read_int(4)
    game_state['read_dialog_option_color'] = align_cursor.read_int(4)
    game_state['stop_dialog_at_end'] = align_cursor.read_int(4)
    game_state['speech_portrait_placement'] = align_cursor.read_int(4)
    game_state['speech_portrait_x'] = align_cursor.read_int(4)
    game_state['speech_portrait_y'] = align_cursor.read_int(4)
    game_state['speech_display_post_time_ms'] = align_cursor.read_int(4)
    game_state['reserved'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=GAME_STATE_RESERVED_INTS)
    game_state['recording'] = align_cursor.read_int(4)
    game_state['playback'] = align_cursor.read_int(4)
    game_state['gamestep'] = align_cursor.read_int(2)
    game_state['randseed'] = align_cursor.read_int(4)
    game_state['player_on_region'] = align_cursor.read_int(4)
    game_state['screen_is_faded_out'] = align_cursor.read_int(4)
    game_state['check_interaction_only'] = align_cursor.read_int(4)
    game_state['bg_frame'] = align_cursor.read_int(4)
    game_state['bg_anim_delay'] = align_cursor.read_int(4)
    game_state['music_vol_was'] = align_cursor.read_int(4)
    game_state['wait_counter'] = align_cursor.read_int(2)
    game_state['mboundx1'] = align_cursor.read_int(2)
    game_state['mboundx2'] = align_cursor.read_int(2)
    game_state['mboundy1'] = align_cursor.read_int(2)
    game_state['mboundy2'] = align_cursor.read_int(2)
    game_state['fade_effect'] = align_cursor.read_int(4)
    game_state['bg_frame_locked'] = align_cursor.read_int(4)
    game_state['global_script_vars'] =\
        align_cursor.read_array_of_ints(
            element_size=4,
            array_size=MAXGSVALUES)
    game_state['cur_music_number'] = align_cursor.read_int(4)
    game_state['music_repeat'] = align_cursor.read_int(4)
    game_state['music_master_volume'] = align_cursor.read_int(4)
    game_state['digital_master_volume'] = align_cursor.read_int(4)
    game_state['walkable_areas_on'] =\
        align_cursor.read_array_of_ints(
            element_size=1,
            array_size=MAX_WALK_AREAS + 1)
    game_state['screen_flipped'] = align_cursor.read_int(2)
    game_state['offsets_locked'] = align_cursor.read_int(2)
    game_state['entered_at_x'] = align_cursor.read_int(4)
    game_state['entered_at_y'] = align_cursor.read_int(4)
    game_state['entered_edge'] = align_cursor.read_int(4)
    game_state['want_speech'] = align_cursor.read_int(4)
    game_state['cant_skip_speech'] = align_cursor.read_int(4)
    game_state['script_timers'] = align_cursor.read_array_of_ints(
            element_size=4,
            array_size=MAX_TIMERS)
    game_state['sound_volume'] = align_cursor.read_int(4)
    game_state['speech_volume'] = align_cursor.read_int(4)
    game_state['normal_font'] = align_cursor.read_int(4)
    game_state['speech_font'] = align_cursor.read_int(4)
    game_state['key_skip_wait'] = align_cursor.read_int(1)
    game_state['swap_portrait_lastchar'] = align_cursor.read_int(4)
    game_state['separate_music_lib'] = align_cursor.read_int(4)
    game_state['in_conversation'] = align_cursor.read_int(4)
    game_state['screen_tint'] = align_cursor.read_int(4)
    game_state['num_parsed_words'] = align_cursor.read_int(4)
    game_state['parsed_words'] = align_cursor.read_array_of_ints(
            element_size=2,
            array_size=MAX_PARSED_WORDS)
    game_state['bad_parsed_word'] = align_cursor.read_array_of_ints(
            element_size=1,
            array_size=100)
    game_state['raw_color'] = align_cursor.read_int(4)
    game_state['raw_modified'] = align_cursor.read_array_of_ints(
            element_size=4,
            array_size=MAX_BSCENE)
    game_state['filenumbers'] = align_cursor.read_array_of_ints(
            element_size=2,
            array_size=MAXSAVEGAMES)
    game_state['room_changes'] = align_cursor.read_int(4)
    game_state['mouse_cursor_hidden'] = align_cursor.read_int(4)
    game_state['silent_midi'] = align_cursor.read_int(4)
    game_state['silent_midi_channel'] = align_cursor.read_int(4)
    game_state['current_music_repeating'] = align_cursor.read_int(4)
    game_state['shakesc_delay'] = align_cursor.read_int(4)
    game_state['shakesc_amount'] = align_cursor.read_int(4)
    game_state['shakesc_length'] = align_cursor.read_int(4)
    game_state['rtint_red'] = align_cursor.read_int(4)
    game_state['rtint_green'] = align_cursor.read_int(4)
    game_state['rtint_blue'] = align_cursor.read_int(4)
    game_state['rtint_level'] = align_cursor.read_int(4)
    game_state['rtint_light'] = align_cursor.read_int(4)
    game_state['end_cutscene_music'] = align_cursor.read_int(4)
    game_state['skip_until_char_stops'] = align_cursor.read_int(4)
    game_state['get_loc_name_last_time'] = align_cursor.read_int(4)
    game_state['get_loc_name_save_cursor'] = align_cursor.read_int(4)
    game_state['restore_cursor_mode_to'] = align_cursor.read_int(4)
    game_state['restore_cursor_image_to'] = align_cursor.read_int(4)
    game_state['music_queue_size'] = align_cursor.read_int(2)
    game_state['music_queue'] = align_cursor.read_array_of_ints(
            element_size=2,
            array_size=MAX_QUEUED_MUSIC)
    game_state['new_music_queue_size'] = align_cursor.read_int(2)
    game_state['crossfading_out_channel'] = align_cursor.read_int(2)
    game_state['crossfade_step'] = align_cursor.read_int(2)
    game_state['crossfade_out_volume_per_step'] = align_cursor.read_int(2)
    game_state['crossfade_initial_volume_out'] = align_cursor.read_int(2)
    game_state['crossfading_in_channel'] = align_cursor.read_int(2)
    game_state['crossfade_in_volume_per_step'] = align_cursor.read_int(2)
    game_state['crossfade_final_volume_in'] = align_cursor.read_int(2)

    game_state['audio_items'] = write_queued_audio_items_aligned(align_cursor)

    game_state['takeover_from'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=50)
    game_state['playmp3file_name'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=PLAYMP3FILE_MAX_FILENAME_LEN)
    game_state['globalstrings'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=MAXGLOBALSTRINGS * MAX_MAXSTRLEN)
    game_state['lastParserEntry'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=MAX_MAXSTRLEN)
    game_state['game_name'] = align_cursor.read_array_of_ints(
        element_size=1,
        array_size=100)
    game_state['ground_level_areas_disabled'] = align_cursor.read_int(4)
    game_state['next_screen_transition'] = align_cursor.read_int(4)
    game_state['gamma_adjustment'] = align_cursor.read_int(4)
    game_state['temporarily_turned_off_character'] = align_cursor.read_int(2)
    game_state['inv_backwards_compatibility'] = align_cursor.read_int(2)
    game_state['gui_draw_order'] = align_cursor.read_int(4, assert_value=0)
    game_state['do_once_tokens'] = align_cursor.read_int(4, assert_value=0)
    game_state['num_do_once_tokens'] = align_cursor.read_int(4)
    game_state['text_min_display_time_ms'] = align_cursor.read_int(4)
    game_state['ignore_user_input_after_text_timeout_ms'] =\
        align_cursor.read_int(4)
    game_state['ignore_user_input_until_time'] = align_cursor.read_int(4)
    game_state['default_audio_type_volumes'] = align_cursor.read_array_of_ints(
        element_size=4,
        array_size=MAX_AUDIO_TYPES)
    align_cursor.finalize()
    return game_state


def write_queued_audio_items_aligned(cursor):
    align_cursor = cursor_module.AlignedCursor(cursor)
    audio_items = []
    for i in range(MAX_QUEUED_MUSIC):
        audio_item = {}
        audio_items.append(audio_item)
        audio_item['audio_clip_index'] = align_cursor.read_int(2)
        audio_item['priority'] = align_cursor.read_int(2)
        audio_item['repeat'] = align_cursor.read_bool(1)
        audio_item['cached'] = align_cursor.read_int(4, assert_value=0)
        align_cursor.finalize()

    return audio_items


def read_room_state(cursor, been_here=None):
    room = {}
    room_align_cursor = cursor_module.AlignedCursor(cursor)
    room['been_here'] = been_here
    if been_here is None or been_here:
        room['been_here_2'] = room_align_cursor.read_bool(4)
        if been_here is not None and been_here != room['been_here_2']:
            raise AssertionError('been_here: {} != {}'.format(
                been_here,
                room['been_here_2']))
        else:
            room['been_here'] = room['been_here_2']

        room['num_objects'] = room_align_cursor.read_int(4)
        room['objects'] = []

        for j in range(MAX_INIT_SPR):
            object_align_cursor = cursor_module.AlignedCursor(
                room_align_cursor)
            x = object_align_cursor.read_array_of_ints(
                element_size=4,
                array_size=3)
            tint = object_align_cursor.read_array_of_ints(
                element_size=2,
                array_size=15)
            cycling = object_align_cursor.read_array_of_ints(
                element_size=1,
                array_size=4)
            blocking_width = object_align_cursor.read_array_of_ints(
                element_size=2,
                array_size=2)
            object_align_cursor.finalize()

            room['objects'].append({
                'x': x,
                'tint': tint,
                'cycling': cycling,
                'blocking_width': blocking_width})
        
        room['flagstates'] = room_align_cursor.read_array_of_ints(
            element_size=2,
            array_size=MAX_FLAGS)
        room['ts_data_size'] = room_align_cursor.read_int(4)
        room['ts_data_0'] = room_align_cursor.read_int(4, assert_value=0)
        room['hotspot_events'] =\
            get_interaction_events(room_align_cursor, MAX_HOTSPOTS)
        room['object_events'] =\
            get_interaction_events(room_align_cursor, MAX_INIT_SPR)
        room['region_events'] =\
            get_interaction_events(room_align_cursor, MAX_REGIONS)
        room['current_room_events'] =\
            get_interaction_events(room_align_cursor, 1)
        room['hotspots_enabled'] = room_align_cursor.read_array_of_ints(
            element_size=1,
            array_size=MAX_HOTSPOTS)
        room['regions_enabled'] = room_align_cursor.read_array_of_ints(
            element_size=1,
            array_size=MAX_REGIONS)
        room['walkbehind_base'] = room_align_cursor.read_array_of_ints(
            element_size=2,
            array_size=MAX_OBJ)
        room['variables'] = room_align_cursor.read_array_of_ints(
            element_size=4,
            array_size=MAX_GLOBAL_VARIABLES)
        room_align_cursor.finalize()
        room['ts_data'] = cursor.read_bytes(room['ts_data_size'])
    return room


def read_room_states(cursor):
    rooms = []
    for i in range(MAX_ROOMS):
        been_here = cursor.read_bool(1)
        rooms.append(read_room_state(cursor, been_here=been_here))
    return rooms

def get_interaction_events(cursor, count):
    events = []
    for j in range(count):
        num_events = cursor.read_int(4)
        event_types = cursor.read_array_of_ints(
            INT_BYTES,
            MAX_NEWINTERACTION_EVENTS)
        times_run = cursor.read_array_of_ints(
            INT_BYTES,
            MAX_NEWINTERACTION_EVENTS)
        responses = [
            cursor.read_int(4) for x in range(MAX_NEWINTERACTION_EVENTS)]
        events.append({
            'num_events': num_events,
            'event_types': event_types,
            'times_run': times_run,
            'responses': responses})
    return events


