import os
import collections

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

import jsonfield
from autoslug import AutoSlugField
from markitup.fields import MarkupField
from model_utils.models import StatusModel, TimeStampedModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from users.models import User
from lib.storage import upload_path
from . import choices


class TaggedArticle(TaggedItemBase):
    content_object = models.ForeignKey('Article')
    tag_type = models.CharField(max_length=50, choices=choices.TAG_TYPES,
        verbose_name=_(u'Tag Type'), default=choices.TAG_TYPES.folksonomic,
        blank=True)


class Article(StatusModel, TimeStampedModel):
    # WARNING: ArticleForm overrides save so that we can save
    # the m2m Contributors relationship. subsequently, save_m2m is
    # not called. If you introduce a new m2m relationship, you must
    # change the save method in ArticleForm.

    def upload_article_callback(self, filename):
        return upload_path('articles', filename)

    def upload_materials_callback(self, filename):
        return upload_path('materials', filename)

    site_owner = models.ForeignKey(User, verbose_name=_(u'Compendia Owner'), help_text=_(u'Site user who owns this compendium'))
    authors_text = models.TextField(verbose_name=_(u'Authors'), help_text=_(u'Authors listed in paper (max length 500)'), max_length=500)
    authorship = jsonfield.JSONField(verbose_name=_(u'Authors'), load_kwargs={'object_pairs_hook': collections.OrderedDict},
        help_text=_(u'Loosely structured info for authorship for authors who do not have site accounts'), default="{}")
    contributors = models.ManyToManyField(User, blank=True, null=True, through='Contributor', related_name='contributors',
        help_text=_(u'ResearchCompendia users who have contributed to this compendium'))
    STATUS = choices.STATUS
    doi = models.CharField(max_length=2000, verbose_name=_(u'DOI'), blank=True,
        help_text=_(u'Please share your paper DOI if applicable'))
    title = models.CharField(max_length=500, verbose_name=_(u'Title'),
        help_text=_(u'Please title your compendium. Does not have to match the title of the paper.'))
    paper_abstract = MarkupField(max_length=5000, blank=True, verbose_name=_(u'Paper Abstract'),
        help_text=_(u'Please share the abstract of the paper. Markdown is allowed. (5000 characters maximum) (Optional)'))
    description_header = models.CharField(max_length=100, verbose_name=_(u'Description heading'), default="Code and Data Abstract")
    code_data_abstract = MarkupField(max_length=5000, blank=True, verbose_name=_(u'Code and Data Abstract'),
        help_text=_(u'Please write an abstract for the code and data. Does not need to match paper abstract.'
                    u'Markdown is allowed. (5000 characters maximum)'))
    journal = models.CharField(blank=True, max_length=500, verbose_name=_(u'Journal Name'),
        help_text=_(u'Please share the name of the journal if applicable'))
    article_url = models.URLField(blank=True, max_length=2000, verbose_name=_(u'Article URL'))
    related_urls = jsonfield.JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, verbose_name=_(u'Related URLs'), default="{}")
    content_license = models.CharField(max_length=100, choices=choices.CONTENT_LICENSES, blank=True)
    code_license = models.CharField(max_length=100, choices=choices.CODE_LICENSES, blank=True)
    compendium_type = models.CharField(max_length=100, choices=choices.ENTRY_TYPES, blank=True)
    primary_research_field = models.CharField(max_length=300, choices=choices.RESEARCH_FIELDS,
        verbose_name=_(u'Primary research field'), blank=True)
    secondary_research_field = models.CharField(max_length=300, choices=choices.RESEARCH_FIELDS,
        verbose_name=_(u'Secondary research field'), blank=True)
    notes_for_staff = models.TextField(max_length=5000, blank=True, verbose_name=_(u'Notes for staff'),
        help_text=_(u'Private notes to the staff for help in creating your research'
                    u'compendium, including links to data and code if not uploaded'))
    article_file = models.FileField(blank=True, upload_to=upload_article_callback,
        help_text=_(u'File containing the article. Size limit for the form is 100MB. '
                    u'Please contact us for larger files.'))
    code_archive_file = models.FileField(blank=True, upload_to=upload_materials_callback,
        help_text=_(u'File containing an archive of the code. Please include a README '
                    u'in the archive according to site recommendations. Size limit for the '
                    u'form is 100MB. Please contact us for larger files.'))
    code_doi = models.CharField(max_length=2000, verbose_name=_(u'cDOI'), blank=True,
        help_text=_(u'this will be the DOI for this code'))
    data_archive_file = models.FileField(blank=True, upload_to=upload_materials_callback,
        help_text=_(u'File containing an archive of the data. Please include a README in the '
                    u'archive according to site recommendations. Size limit for the form is 100MB. '
                    u'Please contact us for larger files.'))
    data_doi = models.CharField(max_length=2000, verbose_name=_(u'dDOI'), blank=True,
        help_text=_(u'this will be the DOI for this code'))

    # The below FileFields were last minute hacks to allow for demos with customized
    # buttons and descriptions for someone. At some point we shouldn't add more columns to this
    # table and rather have a separate table to represent an item that belongs to an Article.

    # The class might have columns like so:
    # FK to Article
    # identifier_type, for examplemple, 'doi', 'issn'
    # resource_type, for example, 'audovisual', 'dataset', software', 'service'
    # uri_scheme, for example, 'http', 'file', 'ftp', 'git'???
    # domain, for example, 'en.wikipedia.org'
    #
    # storage mechanism, file storage, cloud storage, ...

    lecture_notes_archive_file = models.FileField(blank=True, null=True, upload_to=upload_materials_callback,
        verbose_name=_(u'Course Lectures'), help_text=_(u'File containing a an archive of course lecture notes.'))
    homework_archive_file = models.FileField(blank=True, null=True, upload_to=upload_materials_callback,
        verbose_name=_(u'Course Assignments'), help_text=_(u'File containing a an archive of course assignments.'))
    solution_archive_file = models.FileField(blank=True, null=True, upload_to=upload_materials_callback,
        verbose_name=_(u'Course Solutions'), help_text=_(u'File containing a an archive of course solutions.'))
    book_file = models.FileField(blank=True, null=True, upload_to=upload_materials_callback,
        verbose_name=_(u'Book'))
    verification_archive_file = models.FileField(blank=True, null=True, upload_to=upload_materials_callback,
        help_text=_(u'File containing a reviewer created archive that is used for verification.'))
    image_archive_file = models.FileField(blank=True, null=True, upload_to=upload_materials_callback,
        verbose_name=_(u'Image(s)'))

    # deprecated, use article_tags
    tags = TaggableManager(related_name="deprecated_tags", blank=True, help_text=_(u'Deprecated. Use article tags.'))
    legacy_id = models.IntegerField(blank=True, null=True, verbose_name=_(u'RunMyCode ID'), help_text=_(u'Only used for old RunMyCode pages'))
    article_tags = TaggableManager(blank=True,
        through=TaggedArticle,
        help_text=_(u'Share keywords about the research, code and data. For example, use keywords for '
                    u'the languages used in the project code.'))

    # HACK, in the interest of getting a slice of something out quickly i'm adding non-repeating fields
    # from bibtex for journals rather than using the bibjson field for everything/bibjson formatter stuff. a TODO

    month = models.CharField(max_length=500, blank=True,
        help_text=_(u'The month of publication (or, if unpublished, the month of creation)'))
    year = models.CharField(max_length=500, blank=True,
                            help_text=_(u'The year of publication (or, if unpublished, the year of creation)'))
    volume = models.CharField(max_length=500, blank=True, help_text=_(u'The volume of a journal or multi-volume book'))
    number = models.CharField(max_length=500, blank=True,
        help_text=_(u'The "(issue) number" of a journal, magazine, or tech-report, if applicable. '
                    u'(Most publications have a "volume", but no "number" field.)'))
    pages = models.CharField(max_length=500, blank=True,
        help_text=_(u'Page numbers, separated either by commas or double-hyphens.'))

    manual_citation = MarkupField(max_length=500, blank=True, verbose_name=_(u'Manual Citation'),
                                  help_text=_(u'Citation created by ResearchCompendia site admins.'
                                              u'Markdown is allowed. (500 characters maximum)'))

    # Thoughts
    # There are so many different approaches towards storing citation information with an item,
    # and this deserves some discussion. I added this jsonfield as a potential stopgap measure
    # for UI stuff -- the idea was to shove bibliographic information in to a dictionary that
    # could get displayed on the front end according to whatever citation style a user prefers.
    #
    # ultimately, I don't know what you'd want here. You might want to have bibliographic information
    # stored in a graph, you might want to do something less complicated, you may want to create
    # a CitationMixin so that we pull out citation logic in to a mixin class that can be
    # inherited by any class that wants to be citable.
    #
    # Before stomping over things, take a look at the existing work out there on this topic.
    bibjson = jsonfield.JSONField(verbose_name=_(u'Citation in bibjson form'), default="{}")

    admin_notes = MarkupField(max_length=5000, blank=True, verbose_name=_(u'Administrator Notes'),
        help_text=_(u'Notes about the compendia. Markdown is allowed. (5000 characters maximum)'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        # yes, this is not ideal, but that's what they asked for
        year_created = self.created.strftime('%Y')
        return reverse('compendia:year_detail', args=(year_created, self.id,))
        # return reverse('compendia:year_detail', args=(self.id,))

    class Meta(object):
        ordering = ['title']
        verbose_name = _(u'compendium')
        verbose_name_plural = _(u'compendia')


class Contributor(TimeStampedModel):
    # This class never ended up getting used.
    # I wanted to have a way to link ResearchCompendia users to an Article
    # rather than just linking to the page creator.
    user = models.ForeignKey(User, verbose_name=(u'Contributing User'))
    article = models.ForeignKey(Article, verbose_name=_(u'Article'))
    role = models.CharField(max_length=50, choices=choices.CONTRIBUTOR_ROLES,
        verbose_name=_(u'Contributing Role'),
        blank=True)
    citation_order = models.IntegerField(blank=True, null=True, verbose_name=_(u'Citation Order'))

    def __unicode__(self):
        return '%s contributor for %s' % (self.user, self.article)

    class Meta(object):
        ordering = ['citation_order', 'user']
        verbose_name = _(u'contributor')
        verbose_name_plural = _(u'contributors')


class Verification(StatusModel, TimeStampedModel):
    def upload_callback(self, filename):
        return upload_path('results', filename)

    STATUS = choices.VERIFICATION_STATUS
    article = models.ForeignKey(Article, verbose_name=_(u'Article'))
    stdout = models.TextField(blank=True, verbose_name=_(u'Standard output'))
    stderr = models.TextField(blank=True, verbose_name=_(u'Standard error'))
    requestid = models.CharField(max_length=50, verbose_name=_(u'Request ID'), blank=True)
    parameters = jsonfield.JSONField(verbose_name=_(u'Parameters'),
        help_text=_(u'Parameters used during the verification, if the defaults were not used.'),
        default="{}")
    archive_info = jsonfield.JSONField(verbose_name=_(u'Archive information'), default="{}")
    archive_file = models.FileField(blank=True, upload_to=upload_callback,
       help_text=_(u'File containing an archive of the verification results.'))
    slug = AutoSlugField(populate_from='populate_slug', unique_with='article')

    def __unicode__(self):
        return 'verification %s for %s' % (self.id, self.article)

    def archive_base_name(self):
        return os.path.basename(self.archive_file.name)

    def populate_slug(self):
        datestr = self.created.strftime('%Y.%m')
        return '%s.%s' % (datestr, self.id)

    class Meta(object):
        ordering = ['-created']
        verbose_name = _(u'verification')
        verbose_name_plural = _(u'verifications')


class TableOfContentsEntry(models.Model):
    entry_text = models.CharField(max_length=100, help_text=_(u'The text that appears in the table of contents'))
    entry_order = models.IntegerField(help_text=_(u'Order this entry appears in the table of contents'), unique=True)
    description = models.TextField(max_length=500, blank=True, verbose_name=_(u'Description'),
        help_text=_(u'Write an optional descrption to appear with this Table of Contents entry.'
                    u'(500 characters maximum)'))
    slug = AutoSlugField(populate_from='entry_text', editable=True, unique=True)

    def __unicode__(self):
        return self.entry_text

    class Meta(object):
        ordering = ['entry_order']
        verbose_name = _(u'Table of Contents Entry')
        verbose_name_plural = _(u'Table of Contents Entries')


class EntryType(models.Model):
    compendium_type = models.CharField(max_length=100, choices=choices.ENTRY_TYPES, default='misc', unique=True)
    table_of_content = models.ForeignKey(TableOfContentsEntry,
        help_text=_(u'The table of content entry that this compendium type belongs to'))

    def __unicode__(self):
        return self.compendium_type


# TODO this will be removed. it was just a thought experiment
class TableOfContentsOption(models.Model):
    compendium_type = models.CharField(max_length=100, choices=choices.ENTRY_TYPES, default='misc', unique=True)
    description = MarkupField(max_length=500, blank=True, verbose_name=_(u'Description'),
        help_text=_(u'Write an optional descrption to appear with the Table of Contents entry.'
                    u'Markdown is allowed. (500 characters maximum)'))

    def __unicode__(self):
        return self.compendium_type

    class Meta(object):
        verbose_name = _(u'Table of Contents Option')
        verbose_name_plural = _(u'Table of Contents Options')
