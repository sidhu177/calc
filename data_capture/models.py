
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)
from django.utils import timezone

from contracts.models import (Contract, CashField, EDUCATION_CHOICES,
                              MIN_ESCALATION_RATE, MAX_ESCALATION_RATE)


class SubmittedPriceList(models.Model):
    CONTRACTOR_SITE_CHOICES = [
        ('Customer', 'Customer/Offsite'),
        ('Contractor', 'Contractor/Onsite'),
        ('Both', 'Both'),
    ]

    STATUS_UNREVIEWED = 0
    STATUS_APPROVED = 1
    STATUS_RETIRED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (
        (STATUS_UNREVIEWED, 'unreviewed'),
        (STATUS_APPROVED, 'approved'),
        (STATUS_RETIRED, 'retired'),
        (STATUS_REJECTED, 'rejected'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This is the equivalent of Contract.idv_piid.
    contract_number = models.CharField(
        max_length=128,
        help_text='This should be the full contract number, e.g. GS-XXX-XXXX.',
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9-_]+$',
            message='Please use only letters, numbers, and dashes (-).')],
    )
    vendor_name = models.CharField(max_length=128)
    schedule = models.CharField(
        max_length=128
    )
    is_small_business = models.BooleanField()
    contractor_site = models.CharField(
        verbose_name='Worksite',
        choices=CONTRACTOR_SITE_CHOICES,
        max_length=128
    )
    contract_start = models.DateField(
        null=True,
        blank=True,
    )
    contract_end = models.DateField(
        null=True,
        blank=True,
    )
    escalation_rate = models.FloatField(
        verbose_name='escalation rate (%)',
        validators=[MinValueValidator(MIN_ESCALATION_RATE),
                    MaxValueValidator(MAX_ESCALATION_RATE)]
    )

    submitter = models.ForeignKey(User)

    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_UNREVIEWED)
    status_changed_by = models.ForeignKey(User, related_name='+')
    status_changed_at = models.DateTimeField()

    uploaded_filename = models.CharField(
        max_length=128,
        help_text=(
            'Name of the file that was uploaded, as it was called on '
            'the uploader\'s system. For display purposes only.'
        )
    )
    serialized_gleaned_data = models.TextField(
        help_text=(
            'The JSON-serialized data from the upload, including '
            'information about any rows that failed validation.'
        )
    )

    def add_row(self, **kwargs):
        row = SubmittedPriceListRow(**kwargs)
        row.price_list = self
        row.save()
        return row

    def get_schedule_title(self):
        # We're importing here to avoid a circular import. Kinda icky.
        from .schedules.registry import get_class

        return get_class(self.schedule).title

    def get_business_size_string(self):
        # TODO: Based on contracts/docs/s70/s70_data.csv, it seems
        # business size is either 'S' or 'O'. Assuming here that
        # 'S' means 'Small Business' and 'O' means 'Other'
        # but WE REALLY, REALLY NEED TO VERIFY THIS.

        if self.is_small_business:
            return 'S'
        return 'O'

    def _change_status(self, status, user):
        self.status = status
        self.status_changed_at = timezone.now()
        self.status_changed_by = user

    def approve(self, user):
        '''
        Approve this SubmittedPriceList. This causes its rows of pricing data
        to be converted to Contract models, which are then accessible via
        CALC's API and in the Data Explorer.
        '''
        self._change_status(self.STATUS_APPROVED, user)

        for row in self.rows.filter(is_muted=False):
            if row.contract_model is not None:
                raise AssertionError()

            contract = Contract(
                idv_piid=self.contract_number,
                contract_start=self.contract_start,
                contract_end=self.contract_end,
                vendor_name=self.vendor_name,
                labor_category=row.labor_category,
                education_level=row.education_level,
                min_years_experience=row.min_years_experience,
                contractor_site=self.contractor_site,
                schedule=self.get_schedule_title(),
                business_size=self.get_business_size_string(),
                sin=row.sin,
            )

            contract.adjust_contract_year()

            # Assuming the rate in the price list is the 'base rate'
            # Escalate the hourly_rate_yearX fields
            contract.escalate_hourly_rate_fields(
                row.base_year_rate, self.escalation_rate)

            # Update current/next/second year price fields
            contract.update_price_fields()

            contract.full_clean(exclude=['piid'])
            contract.save()
            row.contract_model = contract
            row.save()

        self.save()

    def unreview(self, user):
        '''
        Mark this SubmittedPriceList as "unreviewed" and delete all associated
        Contract models. An "unreviewed" price list is one that has been
        either newly submitted or that has had modifications made to it and
        requires review (to approve or reject it) by an administrator.
        '''
        self._change_status(self.STATUS_UNREVIEWED, user)
        self._delete_associated_contracts()
        self.save()

    def retire(self, user):
        '''
        Mark this SubmittedPriceList as "retired" and delete all associated
        Contract models. Retiring a price list is for removing a once approved
        price list that is now either out-of-date or now otherwise invalid.
        '''
        self._change_status(self.STATUS_RETIRED, user)
        self._delete_associated_contracts()
        self.save()

    def reject(self, user):
        '''
        Reject this SubmittedPriceList. This method should be called on
        "unreviewed" price lists. It is the opposite of approving a price list.
        '''
        if self.status is not self.STATUS_UNREVIEWED:
            raise AssertionError()
        self._change_status(self.STATUS_REJECTED, user)
        self.save()

    def _delete_associated_contracts(self):
        for row in self.rows.all():
            if row.contract_model:
                row.contract_model.delete()
        self.save()

    def __str__(self):
        return "Price List for {}".format(self.contract_number)

    @classmethod
    def get_latest_by_contract_number(cls, contract_number):
        return cls.objects.filter(
            contract_number__iexact=contract_number).latest(
            'status_changed_at')


class SubmittedPriceListRow(models.Model):
    labor_category = models.TextField()
    education_level = models.CharField(
        choices=EDUCATION_CHOICES, max_length=5, null=True,
        blank=True)
    min_years_experience = models.IntegerField()
    base_year_rate = CashField(max_digits=10, decimal_places=2)
    sin = models.TextField(null=True, blank=True)

    is_muted = models.BooleanField(
        help_text=(
            "Whether to include this row in CALC data once its "
            "price list has been approved"
        ),
        default=False
    )

    price_list = models.ForeignKey(
        SubmittedPriceList,
        on_delete=models.CASCADE,
        related_name='rows'
    )

    # If this row is represented in the Contract model objects, this will be
    # non-null. Note that we're explicitly calling it "contract model" here
    # because the Contract model isn't named very accurately: it doesn't
    # really represent a contract, but rather *part* of a contract, so
    # to avoid confusion, we're referring to it as the "contract model".
    contract_model = models.OneToOneField(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        # This is really just so price list rows don't appear as
        # 'SubmittedPriceListRow object' in Django admin.

        return 'Submitted price list row'
