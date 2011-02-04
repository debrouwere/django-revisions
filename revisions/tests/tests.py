from copy import copy
#from utils import TestCase
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
import revisions
from revisions.tests import models

#
# App tests
#

class AppTests(TestCase):
    fixtures = ['revisions_scenario', 'asides_scenario']

    def setUp(self):
        self.story = models.Story.latest.all()[0]

    def test_get_revisions(self):
        raise NotImplementedError
    
    def test_get_next_revision(self):
        next = self.story.get_revisions().next
        self.assertEquals(next, None)

    def test_get_prev_revision(self):
        prev = self.story.get_revisions().prev
        self.assertEquals(prev.vid, 2)

    def test_get_prev_next_revision(self):
        revision_vid = self.story.vid
        prevnext_vid = self.story.get_revisions().prev.get_revisions().next.vid
        self.assertEquals(revision_vid, prevnext_vid)

    def test_id_assignment(self):
        obj = models.Story(
            title = 'this is a title',
            body = 'this is some body text',
            )
        original_obj = copy(obj)
        obj.save()
        saved_obj = obj
        
        # a piece of versioned content is only assigned a bundle id upon the first save
        self.assertFalse(original_obj.id)
        self.assertTrue(saved_obj.id)

    def test_revision_creation(self):
        base = copy(self.story)
        self.story.save()
        revision = self.story
        
        self.assertTrue(base.vid < revision.vid)
        self.assertEquals(base.id, revision.id)
    
    def test_update_old_revision(self):
        old_rev = self.story.get_revisions()[1]
        base = copy(old_rev)
        old_rev.save()
        new = old_rev
        
        self.assertTrue(base.vid < new.vid)
    
    def test_update_old_revision_in_place(self):
        """ It should be possible to update an old revision without creating a 
        new one, for administrative purposes, like updating a last_accessed time. """
        
        revision_count = {
            "before": self.story.get_revisions().count()
            }
        old_rev = self.story.get_revisions()[1]
        old_rev.title = 'Fiddling around with an old revision'
        old_rev.save(new_revision=False)
        revision_count['after'] = self.story.get_revisions().count()
        
        self.assertEquals(revision_count['before'], revision_count['after'])
        
    def test_latest_manager(self):
        """ The latest manager should only display the latest revision
        for each content bundle. """
        
        # see fixtures
        expected = {
            "old_revision_pks": set([1,2,4]),
            "latest_revision_pks": set([3,5]),
            }
        
        actual = {
            "old_revisions": [story for story in models.Story.latest.all() if not 
                story.check_if_latest_revision()],
            "latest_revisions": models.Story.latest.all(),
            "latest_revision_pks": set(models.Story.latest.values_list('pk', flat=True))       
            }

        self.assertEquals(len(expected['latest_revision_pks']), len(actual['latest_revisions']))
        self.assertEquals(expected['latest_revision_pks'], actual['latest_revision_pks'])
        self.assertEquals(actual['latest_revisions'][0].title, 'This is a little story (final)')
        self.assertTrue(expected['old_revision_pks'].isdisjoint(actual['latest_revision_pks']))

    def test_fetch(self):
        # TODO: test schrijven voor pk, date, datetime en het model zelf
        raise NotImplementedError

    def test_revert_to(self):
        older_revision = self.story.get_revisions()[0]
        revision_count = len(self.story.get_revisions())
        reverted_revision = self.story.revert_to(older_revision)
        self.story.save()
        new_revision_count = len(self.story.get_revisions())
        
        # does the reverted revision keep the bundle id intact?
        self.assertEquals(older_revision.id, self.story.id)
        # does it actually revert?
        self.assertEquals(older_revision.body, reverted_revision.body)
        # reverting to an old revision works by making a new one
        self.assertTrue(self.story.vid > older_revision.vid)
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
    
    def test_differ(self):
        raise NotImplementedError

    def test_clear_version_specific_fields(self):
        self.story.prepare_for_writing()
        self.assertEquals(self.story.slug, '')
    
    def test_revisionform(self):
        raise NotImplementedError

class ConcreteInheritanceTests(AppTests):
    fixtures = ['revisions_scenario', 'fancy_revisions_scenario', 'asides_scenario']
    
    def setUp(self):
        self.story = models.FancyStory.latest.all()[0]    

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
        revision_pks = self.story.get_revisions().values_list('pk', flat=True)
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

class ConcreteInheritanceConvenienceTests(ConvenienceTests):
    fixtures = ['revisions_scenario', 'fancy_revisions_scenario', 'asides_scenario']
    
    def setUp(self):
        self.story = models.FancyStory.latest.all()[0]        

class TrashTests(TestCase):
    fixtures = ['trashable_scenario']

    def setUp(self):
        self.story = models.TrashableStory.latest.all()[0]
        self.mgr = models.TrashableStory._default_manager
    
    def test_publicmanager(self):
        self.assertRaises(models.TrashableStory.DoesNotExist, 
            self.mgr.trash.get,
            pk=self.story.pk)
        self.assertTrue(self.mgr.live.get(pk=self.story.pk))
    
    def test_delete_bundle(self):
        story_id = self.story.id
        
        self.story.delete()
        self.assertRaises(models.TrashableStory.DoesNotExist, 
            self.mgr.live.get,
            id=story_id)
        trashed_story = self.mgr.trash.get(id=story_id)
        for story in trashed_story.get_revisions():
            self.assertTrue(story.is_trash)

    def test_delete_permanently(self):
        story_id = self.story.id
        self.story.delete_permanently()
        self.assertRaises(models.TrashableStory.DoesNotExist, 
            self.mgr.get,
            id=story_id)
  
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
        raise NotImplementedError
    
    def test_revisionform(self):
        # tests whether fields specified in Versioning.clear_each_revision
        # (e.g. 'title') are empty as they should be; 
        # client-side counterpart to AppTests.test_revisionform
        
        response = self.c.get('/admin/tests/story/3/')
        self.assertContains(response, '<input id="id_title" type="text" class="vTextField" name="title" maxlength="250" />')