class BaseCondition(object):
    def to_internal_value(self):
        raise NotImplementedError

    def __str__(self):
        return self.to_internal_value()
