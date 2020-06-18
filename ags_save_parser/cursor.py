class AlignedCursor(object):
    def __init__(self, cursor):
        self.cursor = cursor
        self.block = 0
        self.base_alignment = 2
        self.max_alignment = 0
        self.largest_type_size = 8

    def read_bytes(self, count, padding=False):
        if padding:
            self.read_padding(1)
        else:
            self.read_padding(count)
        result = self.cursor.read_bytes(count)
        self.block += count
        return result

    def read_array(
            self,
            element_size,
            array_size,
            look_ahead=False,
            padding_adjustment=0):
        if look_ahead:
            padding_adjustment += self.get_lookahead_padding_adjustment(
                element_size)
            result = self.cursor.read_array(
                element_size,
                array_size,
                look_ahead=look_ahead,
                padding_adjustment=padding_adjustment)
        else:
            self.read_padding(element_size)
            result = self.cursor.read_array(
                element_size,
                array_size)
            self.block += element_size * array_size
        return result

    def read_array_of_ints(self, element_size, array_size, look_ahead=False):
        elements = self.read_array(
            element_size,
            array_size,
            look_ahead=look_ahead)
        array_of_ints = []
        for element in elements:
            array_of_ints.append(
                int.from_bytes(element, byteorder='little'))
        return array_of_ints

    def read_string_from_array_of_ints(
            self,
            element_size,
            array_size,
            look_ahead=False):
        array = self.read_array_of_ints(
            element_size,
            array_size,
            look_ahead)
        end = array.index(0)
        terminated_array = array[0:end]
        string = ''.join([chr(x) for x in terminated_array])
        return string

    def read_padding(self, count):
        if count == 0:
            return

        if count % self.base_alignment == 0:
            pad = self.block % count
            if pad:
                result = self.cursor.read_bytes(count - pad, padding=True)
                #print('padding: {}'.format(result))
                self.block += (count - pad)
        self.max_alignment = max(self.max_alignment, count)
        if self.block % self.largest_type_size == 0:
            self.block = 0

    def get_lookahead_padding_adjustment(self, count):
        if count == 0:
            return

        padding_adjustment = 0
        if count % self.base_alignment == 0:
            pad = self.block % count
            if pad:
                padding_adjustment = count - pad
                padding_adjustment += (
                    self.cursor.get_lookahead_padding_adjustment(1))
        return padding_adjustment

    def read_int(self, length, assert_value=None, signed=False):
        int_bytes = self.read_bytes(length)
        result = int.from_bytes(int_bytes, byteorder='little', signed=signed)
        if assert_value is not None:
            assert result == assert_value
        return result

    def read_bool(self, length):
        bool_int = self.read_int(length)
        if bool_int == 0:
            return False
        elif bool_int == 1:
            return True
        else:
            raise AssertionError(
                'Expected Bool, but not 0 or 1.  Value was {}'.format(
                    bool_int))

    def finalize(self):
        self.read_padding(self.max_alignment)
        self.max_alignment = 0
        self.block = 0

    def read_ahead(self, length):
        self.cursor.read_ahead(length)



class Cursor(object):
    def __init__(self, content_bytes, index=0):
        self.content_bytes = content_bytes
        self.length = len(self.content_bytes)
        self.index = index

    def read_byte(self):
        to_return = self.content_bytes[self.index]
        self.index += 1
        return to_return

    def read_bytes(
            self,
            length,
            padding=False,
            look_ahead=False,
            padding_adjustment=0):
        if not look_ahead:
            padding_adjustment = 0
        index = self.index + padding_adjustment
        end = index + length
        if index > self.length or end > self.length:
            raise AssertionError(
                'Cursor only has length {}, but index was {} '
                'and end was {}'.format(
                    self.length,
                    index,
                    end))
        to_return = self.content_bytes[index:end]
        if not look_ahead:
            self.index = end
        return to_return

    def read_array(
            self,
            element_size,
            array_size,
            look_ahead=False,
            padding_adjustment=0):
        array_bytes = self.read_bytes(
            array_size * element_size,
            look_ahead=look_ahead,
            padding_adjustment=padding_adjustment)
        array_cursor = Cursor(array_bytes, index=0)
        elements = []
        for i in range(array_size):
            elements.append(array_cursor.read_bytes(element_size))
        return elements

    def read_int(self, length, assert_value=None, signed=False):
        int_bytes = self.read_bytes(length)
        result = int.from_bytes(int_bytes, byteorder='little', signed=signed)
        if assert_value is not None:
            assert result == assert_value
        return result

    def read_array_of_ints(self, element_size, array_size, look_ahead=False):
        elements = self.read_array(
            element_size,
            array_size,
            look_ahead=look_ahead)
        array_of_ints = []
        for element in elements:
            array_of_ints.append(
                int.from_bytes(element, byteorder='little'))
        return array_of_ints

    def read_string_from_array_of_ints(
            self,
            element_size,
            array_size,
            look_ahead=False):
        array = self.read_array_of_ints(
            element_size,
            array_size,
            look_ahead)
        end = array.index(0)
        terminated_array = array[0:end]
        string = ''.join([chr(x) for x in terminated_array])
        return string

    def read_string(self, max_length=None, null_terminated=True):
        if max_length is None:
            max_length = len(self.content_bytes) - self.index
        max_length_end = self.index + max_length

        result = []
        while self.index < max_length_end:
            current_byte = self.read_byte()
            if current_byte == 0 and null_terminated:
                break
            else:
                result.append(current_byte)

        return bytes(result)

    def read_bool(self, length):
        bool_int = self.read_int(length)
        if bool_int == 0:
            return False
        elif bool_int == 1:
            return True
        else:
            raise AssertionError(
                'Expected Bool, but not 0 or 1.  Value was {}'.format(
                    bool_int))

    def read_ahead(self, length):
        return list(self.content_bytes[self.index:self.index + length])

    def get_lookahead_padding_adjustment(self, count):
        return 0


