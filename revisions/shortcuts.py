from revisions import models

class VersionedModel(object):
    """
    VersionedModel defines a few common operations (get_revisions, check_if_latest_revision, 
    get_latest_revision) that involve a database lookup. Common practice dictates that
    these should be implemented as methods rather than as properties, because properties
    would signal to the programmer that a simple lookup is taking place.
    
    However, because we value code that feels as natural and domain-driven as possible, 
    and because the database lookups involved are fairly quick queries, we've also included 
    a helper class that implements these common operations as properties -- a few convenient
    shortcuts if you will.
    """

    # REFACTOR: this returns a queryset, so, by analogy with managers, shouldn't this
    # be a property anyway, not just a convenience?
    # (e.g. you can do obj.revisions.filter(...))
    @property
    def revisions(self):
        return self.get_revisions()

    @property
    def is_latest_revision(self):
        return self.check_if_latest_revision()
    
    @property
    def latest_revision(self):
        return self.get_latest_revision()