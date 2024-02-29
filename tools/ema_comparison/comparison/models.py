from django.db import models
import base64
import json
from collections import defaultdict
from datetime import datetime
from enum import unique

import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from comparison.utils import EnumBase
class Software(models.Model):
    @unique
    class Cost(EnumBase):
        CLOSED_SOURCE_COMMERCIAL = {
            "id": 1, "label": "Closed Source - Commercial"
        }
        FOSS = {
            "id": 2, "label": "Free Open-Source"
        }
        CLOSED_SOURCE_FREE = {
            "id": 3, "label": "Free Closed-Source"
        }
        FOSS_WITH_PAID_OPTION = {
            "id": 4, "label": "Free Open-Source w/ Paid Option"
        }

        def __str__(self):
            return self.label

    name = models.CharField(
        verbose_name="Software Name", max_length=200, null=False, blank=False
    )
    developer = models.CharField(
        verbose_name="Developer", max_length=500, null=False, blank=False
    )
    main_website = models.CharField(
        verbose_name="Website", max_length=1000, null=False, blank=False
    )
    other_websites = models.TextField(
        verbose_name="Other Websites",
        help_text=(
            'New-line separated list of other websites affiliated with this '
            'product'
        ),
        null=True,
        blank=True,
    )
    actively_maintained = models.BooleanField(
        verbose_name="Is Actively Maintained?",
        default=True,
    )
    # cost = models.CharField(
    #     choices=sorted([(p.id, str(p)) for p in Role], key=lambda x: x[1]),
    #     default=Role.LEAD_SPECIALIST_IN_TRAINING.id,
    #     null=False,
    #     verbose_name="Cost", max_length=1000, null=False, blank=False
    # )
    # role_id = models.SmallIntegerField(
    #     choices=sorted([(p.id, str(p)) for p in Role], key=lambda x: x[1]),
    #     default=Role.LEAD_SPECIALIST_IN_TRAINING.id,
    #     null=False,
    # )
    # cost_other = 
    base_urls = models.TextField(
        verbose_name="Base URLs",
        help_text=(
            'New-line separated URLs on which the search starts. Each line '
            'must contain a URL. It also can contain the base URL which all '
            'crawled URLs from this URL should start with to be included in '
            'the crawl.'
        ),
        null=True,
        blank=True,
    )
    exclude_urls = models.TextField(
        verbose_name="Exclude URLs",
        help_text='New-line separated URLs to be excluded from the search',
        null=True,
        blank=True,
    )
    is_monitored = models.BooleanField(
        verbose_name="Is Monitored",
        default=True,
    )
    notes = models.TextField(
        verbose_name="Notes",
        null=True,
        blank=True,
    )

    # - Cost: - 
    # - License: -
    # - Server Location: -
    # - Is Monitored: False
    def __str__(self):
        return f"{self.id} - {self.name}"

class Url(models.Model):
    software = models.ForeignKey(
        Software, related_name="urls", on_delete=models.CASCADE
    )
    url = models.CharField(
        verbose_name="Resource URL", max_length=2000, null=False, blank=False
    )
    name = models.CharField(
        verbose_name="Resource URL", max_length=2000, null=False, blank=False
    )
    last_updated = models.DateTimeField(
        verbose_name="Last Updated", null=True, blank=True
    )
    is_monitored = models.BooleanField(
        verbose_name="Is Monitored?",
        default=False,
        null=False,
        blank=False,
    )
    content_length = models.IntegerField(
        verbose_name="Content Length",
        help_text="Content lenght in MD format, removing all new lines",
        null=True,
        blank=True,
        editable=False,
    )
    ai_summary = models.TextField(
        verbose_name="AI Summary",
        help_text='Content Summary (AI-Generated)',
        null=True,
        blank=True,
        editable=False,
    )
    human_summary = models.TextField(
        verbose_name="Human Summary",
        help_text='Content Summary (Human Generated)',
        null=True,
        blank=True,
    )
    content_hash = models.CharField(
        verbose_name="Content Hash",
        max_length=128, null=False, blank=False
    )
    similar_urls = models.TextField(
        verbose_name="Similar URLs",
        help_text='Other URLs which are different that this page, but have the exact same hash.',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.software.name} - {self.url}"