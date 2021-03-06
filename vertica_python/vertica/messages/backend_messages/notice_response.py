

from struct import unpack_from

from vertica_python.vertica.messages.message import BackendMessage


class NoticeResponse(BackendMessage):

    FIELDS_DEFINITIONS = [
        {'type': b'q', 'name': "Internal Query", 'method': 'internal_query'},
        {'type': b'S', 'name': "Severity", 'method': 'severity'},
        {'type': b'M', 'name': "Message", 'method': 'message'},
        {'type': b'C', 'name': "Sqlstate", 'method': 'sqlstate'},
        {'type': b'D', 'name': "Detail", 'method': 'detail'},
        {'type': b'H', 'name': "Hint", 'method': 'hint'},
        {'type': b'P', 'name': "Position", 'method': 'position'},
        {'type': b'W', 'name': "Where", 'method': 'where'},
        {'type': b'p', 'name': "Internal Position", 'method': 'internal_position'},
        {'type': b'R', 'name': "Routine", 'method': 'routine'},
        {'type': b'F', 'name': "File", 'method': 'file'},
        {'type': b'L', 'name': "Line", 'method': 'line'}
    ]

    def FIELDS(self):
        pairs = []
        for field in self.FIELDS_DEFINITIONS:
            pairs.append((field['type'], field['name']))
        return dict(pairs)

    def __init__(self, data):
        self.values = {}

        pos = 0
        while pos < len(data) - 1:
            null_byte = data.find(b'\x00', pos)

            # This will probably work
            unpacked = unpack_from('c{0}sx'.format(null_byte - 1 - pos), data, pos)
            key = unpacked[0]
            value = unpacked[1]

            self.values[self.FIELDS()[key]] = value
            pos += (len(value) + 2)

        # May want to break out into a function at some point
        for field_def in self.FIELDS_DEFINITIONS:
            if self.values.get(field_def['name'], None) is not None:
                setattr(self, field_def['method'], self.values[field_def['name']])

    def error_message(self):
        ordered = []
        for field in self.FIELDS_DEFINITIONS:
            if self.values.get(field['name']) is not None:
                ordered.append("{0}: {1}".format(field['name'], self.values[field['name']]))
        return ', '.join(ordered)


NoticeResponse._message_id(b'N')
