import djclick as click

from contracts.models import Contract


@click.command()
def command():
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
    cmap = {}
    for c in contracts:
        cmap[c.id] = c
    already_visited = {}
    counts = {}
    fields = [
        field for field in Contract._meta.get_fields()
        if not (field.name == 'id' or field.is_relation)
    ]
    for c1 in cmap.values():
        if c1.id in already_visited:
            continue
        c2 = cmap[c1.duplicate_id]
        already_visited[c2.id] = True
        different_fields = tuple([
            field.name for field in fields
            if getattr(c1, field.name) != getattr(c2, field.name)
        ])
        for fieldname in different_fields:
            counts[fieldname] = counts.get(fieldname, 0) + 2
    for k in sorted(counts, key=lambda k: counts[k], reverse=True):
        print("%-25s %d" % (k, counts[k]))
