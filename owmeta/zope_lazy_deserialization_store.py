
class LazyDeserializationStoreDataManager(object):
    def __init__(self, store, transaction_manager=None):
        self.store = store
        self.transaction_manager = transaction_manager

    @property
    def transaction_manager(self):
        return self.__transaction_manager

    @transaction_manager.setter
    def transaction_manager(self, manager):
        self.__transaction_manager = manager
        # Join whatever the current transaction is
        self.__transaction_manager.get().join(self)

    # zope.transaction requires tpc_begin and commit, but there is no point to them since
    # Transaction just calls tpc_begin, commit, and tpc_vote one after the other with
    # nothing important in-between. Due to that, we just implement tpc_vote
    def tpc_begin(self, txn):
        pass

    def commit(self, txn):
        pass

    def tpc_vote(self, txn):
        self.store.tpc_prepare()

    def tpc_finish(self, txn):
        self.store.tpc_commit()

    def tpc_abort(self, txn):
        self.store.tpc_abort()
