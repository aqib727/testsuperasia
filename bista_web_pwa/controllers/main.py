from odoo.http import Controller, request, route
from odoo import http


class PWA(Controller):
    def get_asset_urls(self, asset_xml_id):
        qweb = request.env["ir.qweb"].sudo()
        assets = qweb._get_asset_nodes(asset_xml_id, {}, True, True)
        urls = []
        for asset in assets:
            if asset[0] == "link":
                urls.append(asset[1]["href"])
            if asset[0] == "script":
                urls.append(asset[1]["src"])
        return urls

    @route("/service-worker.js", type="http", auth="public")
    def service_worker(self):
        qweb = request.env["ir.qweb"].sudo()
        urls = []

        urls.extend(self.get_asset_urls("web.assets_common"))
        urls.extend(self.get_asset_urls("web.assets_common_minimal_js"))
        urls.extend(self.get_asset_urls("web.assets_common_lazy"))
        urls.extend(self.get_asset_urls("web.assets_frontend"))
        # urls.extend(self.get_asset_urls("web.assets_frontend_lazy"))
        urls.extend(self.get_asset_urls("web.assets_frontend_minimal_js"))
        urls.extend(self.get_asset_urls("web.assets_backend"))
        version_list = []

        for url in urls:
            version_list.append(url.split("/")[3])
        cache_version = "-".join(version_list)
        mimetype = "text/javascript;charset=utf-8"

        urls.extend([
            "/bista_web_pwa/static/img/online.png",
            "/bista_web_pwa/static/img/offline.png",
            "/offline-fallback",
        ])

        content = qweb.render(
            "bista_web_pwa.service_worker",
            {"pwa_cache_name": cache_version, "pwa_files_to_cache": urls},
        )
        return request.make_response(content, [("Content-Type", mimetype)])

    @route("/bista_web_pwa/manifest.json", type="http", auth="public")
    def manifest(self):
        qweb = request.env["ir.qweb"].sudo()
        config_param = request.env["ir.config_parameter"].sudo()
        pwa_name = config_param.get_param("pwa.manifest.name", "Super Asia")
        pwa_short_name = config_param.get_param("pwa.manifest.short_name", "Super Asia")
        icon128x128 = config_param.get_param(
            "pwa.manifest.icon128x128", "/bista_web_pwa/static/img/icons/icon-128x128.png"
        )
        maskable_icon_x128 = config_param.get_param(
            "pwa.manifest.maskable_icon_x128", "/bista_web_pwa/static/img/icons/maskable_icon_x128.png"
        )
        icon144x144 = config_param.get_param(
            "pwa.manifest.icon144x144", "/bista_web_pwa/static/img/icons/icon-144x144.png"
        )
        maskable_icon_x144 = config_param.get_param(
            "pwa.manifest.maskable_icon_x144", "/bista_web_pwa/static/img/icons/maskable_icon_x144.png"
        )
        icon152x152 = config_param.get_param(
            "pwa.manifest.icon152x152", "/bista_web_pwa/static/img/icons/icon-152x152.png"
        )
        maskable_icon_x152 = config_param.get_param(
            "pwa.manifest.maskable_icon_x152", "/bista_web_pwa/static/img/icons/maskable_icon_x152.png"
        )
        icon192x192 = config_param.get_param(
            "pwa.manifest.icon192x192", "/bista_web_pwa/static/img/icons/icon-192x192.png"
        )
        maskable_icon_x192 = config_param.get_param(
            "pwa.manifest.maskable_icon_x192", "/bista_web_pwa/static/img/icons/maskable_icon_x192.png"
        )
        icon256x256 = config_param.get_param(
            "pwa.manifest.icon256x256", "/bista_web_pwa/static/img/icons/icon-256x256.png"
        )
        maskable_icon_x256 = config_param.get_param(
            "pwa.manifest.maskable_icon_x256", "/bista_web_pwa/static/img/icons/maskable_icon_x256.png"
        )
        icon512x512 = config_param.get_param(
            "pwa.manifest.icon512x512", "/bista_web_pwa/static/img/icons/icon-512x512.png"
        )
        maskable_icon_x512 = config_param.get_param(
            "pwa.manifest.maskable_icon_x512", "/bista_web_pwa/static/img/icons/maskable_icon_x512.png"
        )
        background_color = config_param.get_param(
            "pwa.manifest.background_color", "#bf372b"
        )
        theme_color = config_param.get_param("pwa.manifest.theme_color", "#bf372b")
        mimetype = "application/json;charset=utf-8"
        content = qweb.render(
            "bista_web_pwa.manifest",
            {
                "pwa_name": pwa_name,
                "pwa_short_name": pwa_short_name,
                "icon128x128": icon128x128,
                "maskable_icon_x128": maskable_icon_x128,
                "icon144x144": icon144x144,
                "maskable_icon_x144": maskable_icon_x144,
                "icon152x152": icon152x152,
                "maskable_icon_x152": maskable_icon_x152,
                "icon192x192": icon192x192,
                "maskable_icon_x192": maskable_icon_x192,
                "icon256x256": icon256x256,
                "maskable_icon_x256": maskable_icon_x256,
                "icon512x512": icon512x512,
                "maskable_icon_x512": maskable_icon_x512,
                "background_color": background_color,
                "theme_color": theme_color,
            },
        )
        return request.make_response(content, [("Content-Type", mimetype)])

    @route("/offline-fallback", type="http", auth="public", website=True)
    def offline_fallback(self, **kw):
        return http.request.render('bista_web_pwa.offline_fallback_page', {})

    # @route('/bista_web_pwa/firebase/senderid', type="json", auth="public")
    # def firebase_sender_id(self):
    #     req = request
    #     print(req)
    #     sender_id = self.env['res.config.settings'].sudo().search([('firebase_sender_id')])
    #     print(sender_id)
    #     return str(sender_id)
