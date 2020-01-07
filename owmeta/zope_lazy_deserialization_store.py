
class LazyDeserializationStoreDataManager(object):
    def __init__(self, store, transaction_manager=None):
        self.store = store
        self._needs_to_join = True
        self.transaction_manager = transaction_manager

        def on_modified(store):
            self._rejoin()

        store.watch_for_modifications(on_modified)

    @property
    def transaction_manager(self):
        return self.__transaction_manager

    @transaction_manager.setter
    def transaction_manager(self, manager):
        self.__transaction_manager = manager
        # Join whatever the current transaction is
        self._rejoin()

    def _rejoin(self):
        if self._needs_to_join:
            self.__transaction_manager.get().join(self)
            self._needs_to_join = False

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
        self._needs_to_join = True

    def tpc_abort(self, txn):
        self.store.tpc_abort()
        self._needs_to_join = True

    def abort(self, txn):
        self._needs_to_join = True
