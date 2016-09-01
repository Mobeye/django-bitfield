from __future__ import absolute_import


class BitQueryLookupWrapper(object):
    def __init__(self, alias, column, bit):
        self.table_alias = alias
        self.column = column
        self.bit = bit

    def as_sql(self, qn, connection=None):
        """
        Create the proper SQL fragment. This inserts something like
        "(T0.flags & value) != 0".

        This will be called by Where.as_sql()
        """
        if self.bit:
            return ("(%s.%s | %d)" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                    [])
        return ("(%s.%s & %d)" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                [])

class BitQueryLookupWrapperXor(object):
    pass

try:
    # Django 1.7+
    from django.db.models.lookups import Exact

    class BitQueryLookupWrapper(Exact):  # NOQA
        def process_lhs(self, qn, connection, lhs=None):
            lhs_sql, params = super().process_lhs(
                qn, connection, lhs)
            if self.rhs:
                lhs_sql = lhs_sql + ' & %s'
            else:
                lhs_sql = lhs_sql + ' | %s'
            params.extend(self.process_rhs(qn, connection)[1])
            return lhs_sql, params


    class BitQueryLookupWrapperXor(Exact):  # NOQA
        lookup_name = 'xor'

        def get_rhs_op(self, connection, rhs):
            return '!= 0'

        def process_lhs(self, qn, connection, lhs=None):
            lhs_sql, params = super().process_lhs(
                qn, connection, lhs)
            if self.rhs:
                lhs_sql = lhs_sql + ' & %s'
            else:
                lhs_sql = lhs_sql + ' | %s'
            return lhs_sql, params

except ImportError:
    pass


class BitQuerySaveWrapper(BitQueryLookupWrapper):
    def as_sql(self, qn, connection):
        """
        Create the proper SQL fragment. This inserts something like
        "(T0.flags & value) != 0".

        This will be called by Where.as_sql()
        """

        if self.bit:
            return ("%s.%s | %d" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                    [])
        return ("%s.%s & ~%d" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                [])
