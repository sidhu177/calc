from mimetypes import MimeTypes
import djclick as click

from data_capture import jobs
from contracts.models import BulkUploadContractSource


@click.command()
@click.argument('filename')
def command(filename):
    '''
    Bulk upload the given XLSX file.
    '''

    f = open(filename, 'rb')
    upload_source = BulkUploadContractSource.objects.create(
        has_been_loaded=False,
        original_file=f.read(),
        file_mime_type=MimeTypes().guess_type(filename)[0],
        procurement_center=BulkUploadContractSource.REGION_10
    )
    f.close()

    ok, fails = jobs._process_bulk_upload(upload_source)

    print(f"{ok} contracts successfully proccessed, {fails} failed.")
