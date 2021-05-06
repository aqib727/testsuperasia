===========================
Progressive web application
===========================

Make Odoo an installable Progressive Web Application.

Progressive Web Apps provide an installable, app-like experience on desktop and mobile that are built and delivered directly via the web.
They're web apps that are fast and reliable. And most importantly, they're web apps that work in any browser.
If you're building a web app today, you're already on the path towards building a Progressive Web App.

**Table of contents**

.. contents::
   :local:

Installation
============

After having installed this module, browsing your odoo on mobile you will be able to install it as a PWA.

It is strongly recommended to use this module with a responsive layout, like the one provided by web_responsive.

This module is intended to be used by Odoo back-end users (employees).

When a Progressive Web App is installed, it looks and behaves like all of the other installed apps.
It launches from the same place that other apps launch. It runs in an app without an address bar or other browser UI.
And like all other installed apps, it's a top level app in the task switcher.

In Chrome, a Progressive Web App can either be installed through the three-dot context menu.

This module also provides a "Install PWA" link in Odoo user menu.

Configuration
=============

The following system parameters con be set to customize the appearance of the application

* pwa.manifest.name (defaults to "Odoo PWA")
* pwa.manifest.short_name (defaults to "Odoo PWA")
* pwa.manifest.icon128x128 (defaults to "/bista_web_pwa/static/img/icons/icon-128x128.png")
* pwa.manifest.icon144x144 (defaults to "/bista_web_pwa/static/img/icons/icon-144x144.png")
* pwa.manifest.icon152x152 (defaults to "/bista_web_pwa/static/img/icons/icon-152x152.png")
* pwa.manifest.icon192x192 (defaults to "/bista_web_pwa/static/img/icons/icon-192x192.png")
* pwa.manifest.icon256x256 (defaults to "/bista_web_pwa/static/img/icons/icon-256x256.png")
* pwa.manifest.icon512x512 (defaults to "/bista_web_pwa/static/img/icons/icon-512x512.png")
* Add files to ``FILES_TO_CACHE``
* Evaluate to use a normal JS file for service worker and download data from a normal JSON controller
* Integrate `Notification API <https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification>`_
* Integrate `Web Share API <https://web.dev/web-share/>`_
* Create ``portal_pwa`` module, intended to be used by front-end users (customers, suppliers...)
