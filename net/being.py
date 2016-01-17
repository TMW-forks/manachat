
def job_type(job):
    if (job <= 25 or (job >= 4001 and job <= 4049)):
        return "player"
    elif (job >= 46 and job <= 1000):
        return "npc"
    elif (job > 1000 and job <= 2000):
        return "monster"
    elif (job == 45):
        return "portal"


class Being:
    def __init__(self, being_id, job):
        self.id = being_id
        self._name = ""
        self.job = job
        self.speed = 0

    @property
    def name(self):
        if len(self._name) > 0:
            return self._name
        return "{{ID:" + str(self.id) + "}}"

    @name.setter
    def name(self, newname):
        self._name = newname

    @property
    def type(self):
        return job_type(self.job)

    def __repr__(self):
        return self.name


class BeingsCache:

    def __init__(self, name_request_func):
        self._beings = {}
        self.__getitem__ = self._beings.__getitem__
        self.__delitem__ = self._beings.__delitem__
        self.__iter__ = self._beings.itervalues
        self._name_request_func = name_request_func

    def findId(self, name, type_="player"):
        for id_, being in self._beings.iteritems():
            if being.name == name and being.type == type_:
                return id_
        return -10

    def findName(self, id_, job=1):
        if id_ not in self._beings:
            self._beings[id_] = Being(id_, job)
            if job_type(job) in ("player", "npc"):
                self._name_request_func(id_)
        return self._beings[id_].name
