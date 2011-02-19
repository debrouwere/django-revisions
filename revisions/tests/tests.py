from copy import copy
from django.db import IntegrityError
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import revisions
from revisions.tests import models

#
# App tests
#

class ModelTests(TestCase):
    fixtures = ['revisions_scenario', 'asides_scenario']

    def setUp(self):
        self.story = models.Story.latest.all()[0]

    def test_get_revisions(self, pks=[1,2,3]):
        revisions = self.story.get_revisions()
        self.assertEquals(len(revisions), 3)
        self.assertEquals([rev.pk for rev in revisions], pks)
    
    def test_get_next_revision(self):
        next = self.story.get_revisions().next
        self.assertEquals(next, None)

    def test_get_prev_revision(self, prev_pk=2):
        prev = self.story.get_revisions().prev
        self.assertEquals(prev.pk, prev_pk)

    def test_get_prev_next_revision(self):
        revision_vid = self.story.pk
        prevnext_vid = self.story.get_revisions().prev.get_revisions().next.pk
        self.assertEquals(revision_vid, prevnext_vid)

    def test_id_assignment(self):
        obj = self.story.__class__(
            title = 'this is a title',
            body = 'this is some body text',
            )
        original_obj = copy(obj)
        obj.save()
        saved_obj = obj
        
        # a piece of versioned content is only assigned a bundle id upon the first save
        self.assertFalse(original_obj.cid)
        self.assertTrue(saved_obj.cid)

    def test_revision_creation(self):
        revision = self.story.revise()  
        self.assertTrue(self.story.comparator < revision.comparator)
        self.assertEquals(self.story.cid, revision.cid)
    
    def test_update_old_revision(self):
        base = self.story.get_revisions()[1]
        new = base.revise()
        
        self.assertTrue(base.comparator < new.comparator)
    
    def test_update_old_revision_in_place(self):
        """ It should be possible to update an old revision without creating a 
        new one, for administrative purposes, like updating a last_accessed time. """
        
        revision_count = {
            "before": self.story.get_revisions().count()
            }
        old_rev = self.story.get_revisions()[1]
        old_rev.title = 'Fiddling around with an old revision'
        old_rev.save()
        revision_count['after'] = self.story.get_revisions().count()
        
        self.assertEquals(revision_count['before'], revision_count['after'])
        
    def test_latest_manager(self, expected=None):
        """ The latest manager should only display the latest revision
        for each content bundle. """
        
        # see fixtures
        if not expected:
            expected = {
                "old_revision_pks": set([1,2,4]),
                "latest_revision_pks": set([3,5]),
                }
        
        actual = {
            "old_revisions": [story for story in self.story.__class__.latest.all() if not 
                story.check_if_latest_revision()],
            "latest_revisions": self.story.__class__.latest.all(),
            "latest_revision_pks": set([story.pk for story in self.story.__class__.latest.only(self.story.pk_name).all()])       
            }
        
        self.assertEquals(len(expected['latest_revision_pks']), len(actual['latest_revisions']))
        self.assertEquals(expected['latest_revision_pks'], actual['latest_revision_pks'])
        self.assertEquals(actual['latest_revisions'][0].title, 'This is a little story (final)')
        self.assertTrue(expected['old_revision_pks'].isdisjoint(actual['latest_revision_pks']))

    def test_fetch_by_pk(self, pk=2):
        story = self.story.__class__.fetch(pk)
        self.assertEquals(story.pk, pk)

    def test_revert_to(self):
        older_revision = self.story.get_revisions()[0]
        revision_count = len(self.story.get_revisions())
        reverted_revision = self.story.revert_to(older_revision)
        self.story.revise()
        new_revision_count = len(self.story.get_revisions())
        
        # does the reverted revision keep the bundle id intact?
        self.assertEquals(older_revision.cid, self.story.cid)
        # does it actually revert?
        self.assertEquals(older_revision.body, reverted_revision.body)
        # reverting to an old revision works by making a new one
        self.assertTrue(self.story.comparator > older_revision.comparator)
        self.assertTrue(revision_count < new_revision_count)

    def test_make_current_revision(self):
        latest_revision = self.story
        older_revision = self.story.get_revisions()[1]
        older_revision.make_current_revision()
        new_latest_revision = older_revision
        
        # note to self: zeker maken dat deze effectief verschillen in de fixture, 
        # zodat deze nieuwe revisie effectief goed gekopieerd moet zijn om deze
        # test te doen slagen -- anders heeft het geen zin
        self.assertEquals(older_revision.title, new_latest_revision.title)
        self.assertNotEqual(latest_revision.title, new_latest_revision.title)

    def test_clear_version_specific_fields(self):
        self.story.prepare_for_writing()
        self.assertEquals(self.story.slug, '')

class InheritanceTests(ModelTests):
    fixtures = ['revisions_scenario', 'fancy_revisions_scenario', 'asides_scenario']
    
    def setUp(self):
        self.story = models.FancyStory.latest.all()[0]    

class BaseModelTests(ModelTests):
    fixtures = ['basemodel_revisions_scenario', 'asides_scenario', ]
    
    def setUp(self):
        self.story = models.ManualStory.latest.all()[0]        

class UUIDModelTests(ModelTests):
    fixtures = ['uuidmodel_revisions_scenario', 'asides_scenario', ]
    
    def setUp(self):
        self.story = models.UUIDStory.latest.all()[0]

    def test_fetch_by_pk(self):
        super(UUIDModelTests, self).test_fetch_by_pk("def")

    def test_get_revisions(self):
        super(UUIDModelTests, self).test_get_revisions(["abc", "def", "ghi"])

    def test_get_prev_revision(self):
        super(UUIDModelTests, self).test_get_prev_revision("def")

    def test_latest_manager(self):
        expected = {
            "old_revision_pks": set(["abc","def","aaa"]),
            "latest_revision_pks": set(["ghi","bbb"]),
            }
        super(UUIDModelTests, self).test_latest_manager(expected)   

class FancyBaseModelTests(ModelTests):
    fixtures = ['basemodel_revisions_scenario', 'basemodel_fancy_revisions_scenario', 'asides_scenario', ]

    def setUp(self):
        self.story = models.FancyManualStory.latest.all()[0]

class UniquenessTests(TestCase):
    def setUp(self):
        self.story = models.UniqueStory(title="hello", body="there")
        self.story.save()
    
    def test_per_version_unique_together(self):
        self.assertRaises(IntegrityError, self.story.revise)

    def test_per_bundle_unique_together(self):
        # shouldn't raise an error
        self.story.title = "hola"
        self.story.revise()
        # this shouldn't either, because title and slug are unique_together per bundle (see UniqueStory.Versioning)
        story = models.UniqueStory(title="hey", slug="hey", body="you")
        story.save()
        story.body = "yonder"
        story.revise()
        # and for that same reason, this new story _should_ raise an IntegrityError
        new_story = models.UniqueStory(title="hey", slug="hey")
        self.assertRaises(IntegrityError, new_story.save)      

    def test_per_bundle_unique(self):
        # body is unique per bundle, and we've used "there" before, 
        # so this won't work
        new_story = models.UniqueStory(title="howdy", body="there")
        self.assertRaises(IntegrityError, new_story.save)

class ForeignKeyTests(TestCase):
    fixtures = ['revisions_scenario', ]
    
    def setUp(self):
        self.story = models.Story.latest.all()[0]
    
    def test_foreign_key_to_bundle(self):
        info = models.InfoToBundle(content="Something something.", story=self.story)
        info.save() 

class ConvenienceTests(TestCase):
    fixtures = ['revisions_scenario', 'asides_scenario']

    def setUp(self):
        self.story = models.Story.latest.all()[0]

    def test_get_related_objects(self):
        # we first count all the asides for this particular revision, and then
        # the amount of asides that are related to the content bundle as a whole
        # the fixtures are configured in such a way that there are fk-linked
        # items to multiple versions of the same story, so this count should differ
        #
        # We test out three ways of doing the same thing. 
        # All three should behave identically.
        related_manager = self.story.aside_set
        revision_pks = [rev.pk for rev in self.story.get_revisions().only(self.story.comparator_name).all()]
        asides = related_manager
        total_asides = self.story._get_related_objects(related_manager)
        total_asides_alt = models.Aside.latest.filter(story__in=revision_pks)
        
        self.assertTrue(total_asides.count() > asides.count())
        self.assertEquals(asides.count(), 1)
        self.assertEquals(total_asides.count(), 3)
        
        # we're comparing whether these two approaches to getting all the related objects
        # return the same stuff, not whether they return it in the same order --
        # that's why we compare sets, not lists.
        self.assertEquals(set(total_asides), set(total_asides_alt))

    def test_get_attribute_history(self):
        # get_attribute_history should be entirely functionally equivalent
        # to the list comprehension below
        body_revisions = [(story.body, story) for story in self.story.get_revisions()]
        body_revisions_shortcut = story._get_attribute_history('body')
        
        self.assertEquals(body_revisions, body_revisions_shortcut)

    def test_getattr_history(self):
        """ This just tests the getattr magic, which is a shortcut to
        _get_attribute_history, which is tested separately. """

        self.assertEquals(self.story.body_history, self.story._get_attribute_history('body'))

    def test_getattr_related(self):
        """ This just tests the getattr magic, which is a shortcut to
        _get_related_objects, which is tested separately. """
        
        without_getattr = self.story._get_related_objects(self.story.aside_set)
        with_getattr = self.story.related_aside_set
        
        self.assertEquals(set(without_getattr), set(with_getattr))

    def test_convenience_shortcuts(self):
        regular = self.story
        short = models.ConvenientStory.objects.get(pk=regular.pk)

        self.assertEquals(regular.get_revisions()[1].title, short.revisions[1].title)
        self.assertNotEquals(regular.get_revisions()[1].title, short.revisions[2].title)

class InheritanceConvenienceTests(ConvenienceTests):
    fixtures = ['revisions_scenario', 'fancy_revisions_scenario', 'asides_scenario']
    
    def setUp(self):
        self.story = models.FancyStory.latest.all()[0]        

class TrashTests(TestCase):
    fixtures = ['trashable_scenario']

    def setUp(self):
        self.story = models.TrashableStory.latest.all()[0]
        self.mgr = models.TrashableStory._default_manager
    
    def test_publicmanager(self):
        self.assertRaises(self.story.__class__.DoesNotExist, 
            self.mgr.trash.get,
            pk=self.story.pk)
        self.assertTrue(self.mgr.live.get(pk=self.story.pk))
    
    def test_delete_bundle(self):
        story_id = self.story.cid
        
        self.story.delete()
        self.assertRaises(self.story.__class__.DoesNotExist, 
            self.mgr.live.get,
            cid=story_id)
        trashed_story = self.mgr.trash.get(cid=story_id)
        for story in trashed_story.get_revisions():
            self.assertTrue(story.is_trash)

    def test_delete_permanently(self):
        story_id = self.story.cid
        self.story.delete_permanently()
        self.assertRaises(self.story.__class__.DoesNotExist, 
            self.mgr.get,
            cid=story_id)

class InheritanceTrashTests(TrashTests):
    fixtures = ['trashable_scenario', 'fancy_trashable_scenario']
    
    def setUp(self):
        self.story = models.FancyTrashableStory.latest.all()[0]
        self.mgr = models.FancyTrashableStory._default_manager

#
# Browser tests
#

users = [
    # Stan is a superuser
    {"username": "Stan", "password": "green pastures"},
    # Fred has pretty much no permissions whatsoever
    {"username": "Fred", "password": "pastures of green"},
    ]

class BrowserTests(TestCase):
    fixtures = ['revisions_scenario', 'users']
    apps = (
        'revisions',
        'revisions.tests',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',
        )
    urls = 'revisions.tests.urls'
    
    def setUp(self):
        # some objects we might use directly, instead of via the client
        self.story = models.Story.objects.all()[0]
        user_objs = User.objects.all()
        self.user, self.alt_user = user_objs
        # client setup
        self.c = Client()
        self.c.login(**users[0])
        self.data = {
            'body': u'Hello there!', 
            'small_change': False,
            'title': u'Little big story',
            'aside_set-TOTAL_FORMS': 0,
            'info_set-TOTAL_FORMS': 0,
            'aside_set-INITIAL_FORMS': 0,
            'info_set-INITIAL_FORMS': 0,
            }
    
    def test_save_revision(self):
        response = self.c.post('/admin/tests/story/3/', self.data, follow=True)
        self.assertContains(response, '<a href="6/">Little big story</a>')
    
    def test_save_and_continue_redirect_middleware(self):
        # This test is failing for me, though it works when testing manually
        # Some aspect of middleware testing I'm unaware of?
        
        self.data.update({'_continue': True})
        response = self.c.post('/admin/tests/story/3/', self.data, follow=True)
        self.assertRedirects(response, '/admin/tests/story/6/')
    
    def test_frontend_redirects(self):
        # utils redirects testen in browser
        raise NotImplementedError()
    
    def test_revisionform(self):
        # tests whether fields specified in Versioning.clear_each_revision
        # (e.g. 'title') are empty as they should be; 
        # client-side counterpart to ModelTests.test_revisionform
        
        response = self.c.get('/admin/tests/story/3/')
        self.assertContains(response, '<input id="id_title" type="text" class="vTextField" name="title" maxlength="250" />')