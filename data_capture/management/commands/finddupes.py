import djclick as click

from contracts.models import Contract


@click.command()
def command():
    help='''\
    Finds duplicates across sin, contractor_site, education level, min years of experience, second year price,
    hourly rate year 2, hourly rate year 5, next year price, hourly rate year 3, hourly rate year 4, contract year.
    
    This code assumes, vendor name, labor category, individual piid and current price are the same.
 
    example run (from root directory of calc):

    python manage.py finddupes

    result:

    sin                       2820
    contractor_site           844
    education_level           206
    min_years_experience      142
    second_year_price         8
    hourly_rate_year2         8
    hourly_rate_year5         8
    next_year_price           8
    hourly_rate_year3         6
    hourly_rate_year4         4
    contract_year             4
    '''
    identical_fields = [
        'vendor_name',
        'labor_category',
        'idv_piid',
        'current_price',
    ]
    contracts = Contract.objects.raw(
        'SELECT c1.*, '
        'c2.id AS duplicate_id '
        'FROM %(table)s as c1, %(table)s as c2 '
        'WHERE c1.id != c2.id '
        'AND %(identical_fields)s' % {
            'table': Contract._meta.db_table,
            'identical_fields': ' AND '.join([
                'c1.%(col)s = c2.%(col)s' % {
                    'col': Contract._meta.get_field(field).column
                } for field in identical_fields
            ])
        }
    )

    contract_map = {}
    for c in contracts:
        contract_map[c.id] = c
    already_visited = {}
    counts = {}
    fields = [
        field for field in Contract._meta.get_fields()
        if not (field.name == 'id' or field.is_relation)
    ]
    for c1 in contract_map.values():
        if c1.id in already_visited:
            continue
        c2 = contract_map[c1.duplicate_id]
        already_visited[c2.id] = True
        different_fields = tuple([
            field.name for field in fields
            if getattr(c1, field.name) != getattr(c2, field.name)
        ])
        for fieldname in different_fields:
            counts[fieldname] = counts.get(fieldname, 0) + 2
    for k in sorted(counts, key=lambda k: counts[k], reverse=True):
        print("%-25s %d" % (k, counts[k]))
