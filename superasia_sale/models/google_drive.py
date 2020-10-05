# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import urllib.parse

import csv
import xlrd

import requests

from odoo import api, fields, models
from odoo.exceptions import RedirectWarning, UserError
from odoo.tools.translate import _

from odoo.addons.google_account.models.google_service import GOOGLE_TOKEN_ENDPOINT, TIMEOUT

from tempfile import TemporaryDirectory

_logger = logging.getLogger(__name__)


class GoogleDrive(models.Model):
    _inherit = 'google.drive.config'

    transfer_only = fields.Boolean(string='Is Transfer Template', default=False)

    @api.model
    def get_drive_folder_id(self, folder_name):
        if not folder_name:
            return ''

        access_token = self.get_access_token()

        search_q = "title='%s'" % folder_name
        q_string_format = urllib.parse.quote(search_q)

        request_url = "https://www.googleapis.com/drive/v2/files?q=%s&access_token=%s" % (q_string_format, access_token)
        headers = {"Content-type": "application/x-www-form-urlencoded"}

        try:
            req = requests.get(request_url, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            parents_dict = req.json()
        except requests.HTTPError:
            raise UserError(_("The Folder with name %s cannot be found. Maybe it has been deleted.") % folder_name)

        if parents_dict['items']:
            parent_info = parents_dict['items'][0]
            folder_id = parent_info.get('id')
            return folder_id
        else:
            raise UserError(_("There is no Folder ID for %s. Maybe it has been deleted.") % folder_name)

    @api.model
    def get_handshake_drive_orders(self, folder_id):
        orders_data = []
        # Get the children of the current folder
        if folder_id:
            access_token = self.get_access_token()
            headers = {"Content-type": "application/x-www-form-urlencoded"}
            children_url = "https://www.googleapis.com/drive/v2/files/%s/children?access_token=%s" % (folder_id, access_token)
            try:
                req = requests.get(children_url, headers=headers, timeout=TIMEOUT)
                req.raise_for_status()
                children_response = req.json()
                children_files = children_response.get('items')
            except requests.HTTPError:
                _logger.error("Failed to import from '%s' folder from google drive, got HTTP error: %s",
                              folder_id, requests.HTTPError)

            for child in children_files:
                access_token = self.get_access_token()
                child_url = "%s?access_token=%s" % (child.get('childLink'), access_token)

                try:
                    req = requests.get(child_url, headers=headers, timeout=TIMEOUT)
                    req.raise_for_status()
                    child_response = req.json()
                except requests.HTTPError:
                    _logger.error("Failed to import from '%s' child folder from google drive, got HTTP error: %s",
                                  child.get('childLink'), requests.HTTPError)

                download_url = child_response.get('downloadUrl')
                access_token = self.get_access_token()

                auth_token = "Bearer %s" % access_token
                auth_headers = {"Authorization": auth_token}
                data_lines = []

                # If there is a download url and the document has not been 'deleted'
                if download_url and not child_response.get('explicitlyTrashed'):
                    try:
                        req = requests.get(download_url, headers=auth_headers, timeout=TIMEOUT)
                        req.raise_for_status()
                        content = req.content
                    except requests.HTTPError:
                        _logger.error("Failed to download from '%s' download url from google drive, got HTTP error: %s",
                                      download_url, requests.HTTPError)

                    if content:
                        mime_type = child_response.get('mimeType')
                        if mime_type == 'text/csv':
                            with TemporaryDirectory() as temp_dir:
                                with open(temp_dir + '/' + 'temp.csv', mode='wb+') as temp_file:
                                    temp_file.write(content)

                                with open(temp_dir + '/' + 'temp.csv', mode='r') as open_file:
                                    reader = csv.DictReader(open_file)
                                    data_lines = list(reader)

                        elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mime_type == 'application/vnd.ms-excel':
                            book = xlrd.open_workbook(file_contents=content)

                            sheet = book.sheet_by_index(0)

                            headers_vals = sheet.row_values(0)
                            for row in range(1, sheet.nrows):
                                items = dict(zip(headers_vals, sheet.row_values(row)))
                                data_lines.append(items)
                        else:
                            _logger.warn("Failed to import '%s' from google drive, this '%s' file type is not supported.",
                                         child_response.get('originalFilename'), mime_type)
                if data_lines:
                    orders_data.append(data_lines)
        return orders_data

    @api.model
    def push_handshake_drive_files(self, folder_id, file_path, filename):
        if folder_id:
            access_token = self.get_access_token()

            auth_token = "Bearer %s" % access_token
            auth_headers = {"Authorization": auth_token}

            para = {
                "name": filename,
                "parents": [folder_id]
            }
            files = {
                'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
                'file': open(file_path, mode="rb")
            }
            try:
                req = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers=auth_headers,
                    files=files
                )
                req.raise_for_status()
            except requests.HTTPError:
                _logger.error("Failed to export '%s' to google drive, got HTTP error: %s",
                              filename, requests.HTTPError)
        return True
