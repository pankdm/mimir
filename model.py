
import json

class Mark:
    YES = "YES"
    NO = "NO"
    DONT_KNOW = "DONT_KNOW"
    UNDEFINED = "UNDEFINED"

MarkValues = [Mark.YES, Mark.NO, Mark.DONT_KNOW, Mark.UNDEFINED]

class Query:
    def __init__(self, text, freq):
        self.text = text
        self.freq = freq

class Queries:
    def __init__(self):
        self.q = {}

    def add(self, text, freq):
        query = Query(text, freq)
        self.q[query.text] = query

    def _to_python(self):
        output = {}
        for k, v in self.q.items():
            output[k] = v.freq
        return output
    
    def _from_python(self, data):
        self.q = {}
        for k, v in data.items():
            self.add(k, v)

class Filter:
    def __init__(self, regexp, mark):
        self.regexp = regexp
        self.mark = mark

class Filters:
    def __init__(self):
        self.f = {}

    def set(self, regexp, mark):
        flt = Filter(regexp, mark)
        self.f[regexp] = flt

    def remove(self, regexp):
        del self.f[regexp]

    def _to_python(self):
        output = {}
        for k, v in self.f.items():
            output[k] = v.mark
        return output
    
    def _from_python(self, data):
        self.f = {}
        for k, v in data.items():
            self.set(k, v)

class ManualMarks:
    def __init__(self):
        self.m = {}

    def add(self, text, mark):
        if mark != Mark.UNDEFINED:
            self.m[text] = mark
        else:
            self.remove(text)

    def remove(self, text):
        del self.m[text]

    def _to_python(self):
        return self.m
    
    def _from_python(self, data):
        self.m = data

class GodClass:
    def __init__(self):
        self._clear()
    
    def _clear(self):
        self.qs = Queries()
        self.fs = Filters()
        self.ms = ManualMarks()
        self.target_sense = ""

    def get_filter_mark_for_query(self, text):
        for flt in self.fs.f.values():
            if flt.regexp in text:
                return flt.mark
        return Mark.UNDEFINED

    def get_manual_mark_for_query(self, text):
        if text in self.ms.m:
            return self.ms.m[text]
        return Mark.UNDEFINED

    def get_total_mark_for_query(self, text):
        mark = self.get_manual_mark_for_query(text)
        if mark != Mark.UNDEFINED: return mark
        mark = self.get_filter_mark_for_query(text)
        return mark

    def get_queries(self):
        return self.qs.q.values()

    def get_filters(self):
        return self.fs.f.values()

    def add_query(self, text, freq):
        self.qs.add(text, freq)

    def mark_single_query(self, text, mark):
        self.ms.add(text, mark)

    def remove_mark(self, text):
        self.ms.remove(text)

    def set_filter(self, regexp, mark):
        self.fs.set(regexp, mark)

    def remove_filter(self, regexp):
        self.fs.remove(regexp)

    def set_target_sense(self, sense):
        self.target_sense = sense

    def load_raw_queries(self, file_name):
        self._clear()
        with open(file_name, 'rt') as f:
            for line in f.readlines():
                text, freq = line.decode('utf8').strip('\n').split('\t')
                freq = int(freq)
                self.add_query(text, freq)

    def save_to_file(self, file_name):
        with open(file_name, 'wt') as f:
            data = self._to_python()
            json_string = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            f.write(json_string.encode('utf8'))

    def load_from_file(self, file_name):
        self._clear()
        with open(file_name, 'rt') as f:
            json_string = f.read()
            data = json.loads(json_string.decode('utf8'))
            self._from_python(data)

    def _to_python(self):
        output = {}
        output['queries'] = self.qs._to_python()
        output['filters'] = self.fs._to_python()
        output['marks'] = self.ms._to_python()
        output['target_sense'] =  self.target_sense
        return output

    def _from_python(self, data):
        self.qs._from_python(data.get('queries', {}))
        self.fs._from_python(data.get('filters', {}))
        self.ms._from_python(data.get('marks', {}))
        self.target_sense = data['target_sense']

