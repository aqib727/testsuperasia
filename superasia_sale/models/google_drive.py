# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import json
import re
import urllib.parse
import io
import pprint
import csv
import xlrd

import requests
import werkzeug.urls

from odoo import api, fields, models
from odoo.exceptions import RedirectWarning, UserError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

from odoo.addons.google_account.models.google_service import GOOGLE_TOKEN_ENDPOINT, TIMEOUT

_logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class GoogleDrive(models.Model):

    _inherit = 'google.drive.config'

    transfer_only = fields.Boolean(string='Is Transfer Template', default=False)

    @api.model
    def test_access(self):
        google_web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token = self.get_access_token()

        print(access_token)
        q_string = 'title%3D%27hello%27'
        search_q = "title='Test Sale Order'"

        q_string_format = urllib.parse.quote(search_q)

        request_url = "https://www.googleapis.com/drive/v2/files?q=%s&access_token=%s" % (q_string_format, access_token)
        headers = {"Content-type": "application/x-www-form-urlencoded"}

        try:
            req = requests.get(request_url, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            parents_dict = req.json()
            pp.pprint(parents_dict)
        except requests.HTTPError:
            #TODO: update all user error
            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

        if parents_dict['items']:
            parent_info = parents_dict['items'][0]
            folder_id = parent_info.get('id')

            # Get the children of the current folder
            if folder_id:
                access_token = self.get_access_token()
                children_url = "https://www.googleapis.com/drive/v2/files/%s/children?access_token=%s" % (folder_id, access_token)
                try:
                    req = requests.get(children_url, headers=headers, timeout=TIMEOUT)
                    req.raise_for_status()
                    children_response = req.json()
                    children_files = children_response.get('items')
                    pp.pprint(children_files)

                except requests.HTTPError:
                    raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

                for child in children_files:
                    access_token = self.get_access_token()
                    child_url = "%s?access_token=%s" % (child.get('childLink'), access_token)

                    try:
                        req = requests.get(child_url, headers=headers, timeout=TIMEOUT)
                        req.raise_for_status()
                        child_response = req.json()
                        pp.pprint(child_response)

                    except requests.HTTPError:
                        raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

                    download_url = child_response.get('downloadUrl')
                    # export_links = child['exportLinks']
                    access_token = self.get_access_token()
                    auth_token = "Bearer %s" % (access_token)
                    headers = {"Authorization": auth_token}
                    data_lines = []
                    if download_url:
                        auth_download_url = "%s&access_token=%s" % (download_url, access_token)
                        try:
                            req = requests.get(download_url, headers=headers, timeout=TIMEOUT)
                            req.raise_for_status()
                            content = req.content
                            pp.pprint(content)

                            # content = io.BytesIO(self._DownloadFromUrl(download_url))

                        except requests.HTTPError:
                            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

                        if content:
                            mime_type = child_response.get('mimeType')
                            if mime_type == 'text/csv':
                                # TODO: make temp directory?
                                with open('temp.csv', mode='wb+') as temp_file:
                                    temp_file.write(content)

                                with open('temp.csv', mode='r') as temp_file:
                                    reader = csv.DictReader(temp_file)
                                    data_lines = list(reader)

                            elif mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mime_type == 'application/vnd.ms-excel':
                                print("add xlsx support here")
                                with open('temp.xlsx', mode='wb+') as temp_file:
                                    temp_file.write(content)

                                with open('temp.xlsx', mode='r') as temp_file:
                                    book = xlrd.open_workbook(file_contents=temp_file)
                                    sheet = book.sheet_by_index(0)

                                    headers = sheet.row_values(0)
                                    for row in range(1, sheet.nrows):
                                        items = dict(zip(headers, sheet.row_values(row)))

                                        data_lines.append(items)




            return data_lines


            # elif export_links and export_links.get(mimetype):
            #     self.content = io.BytesIO(
            #         self._DownloadFromUrl(export_links.get(mimetype)))
            #     self.dirty['content'] = False

