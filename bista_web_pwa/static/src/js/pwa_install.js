if ("serviceWorker" in navigator) {
    console.log("Service Worker found in navigator.");
    window.addEventListener("load", function() {
        console.log("Attempting Service Worker registration");
        navigator.serviceWorker.register("/service-worker.js").then(function(reg) {
            console.log("Service worker registered.", reg);
        }).catch((err) => console.log("Service Worker not registered.", err));
    });
}

let deferredPrompt;
// const insPwaBtn = document.querySelector('.install_pwa_btn');
// insPwaBtn.style.display = 'none';
const insPwaBtn = document.querySelectorAll('.install_pwa_btn');
insPwaBtn.forEach(item => {item.style.display = 'none'});

window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent Chrome 67 and earlier from automatically showing the prompt
      e.preventDefault();
      // Stash the event so it can be triggered later.
      deferredPrompt = e;
      // Update UI to notify the user they can add to home screen
      // insPwaBtn.style.display = 'block';
      insPwaBtn.forEach(item => {item.style.display = 'block'});
      // floatingInsPwaBtn.style.display = 'block';
});

// insPwaBtn.addEventListener('click', (e) => {
insPwaBtn.forEach(item => {
    item.addEventListener('click', (e) => {
        // hide our user interface that shows our A2HS button
        // insPwaBtn.style.display = 'none';
        insPwaBtn.forEach(item => {item.style.display = 'none'});
        // Show the prompt
        deferredPrompt.prompt()
            .then(res => console.log(res))
            .catch(error => console.log(error));
        // Wait for the user to respond to the prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt');
            } else {
                console.log('User dismissed the A2HS prompt');
            }
            deferredPrompt = null;
        });
    })
});

odoo.define("bista_web_pwa.systray.install", ['web.UserMenu', 'web.ajax'], function(require) {
    "use strict";

    var UserMenu = require("web.UserMenu");
    // const ajax = require('web.ajax');

    // if ("serviceWorker" in navigator) {
    //     console.log("Service Worker found in navigator.")
    //     window.addEventListener("load", function() {
    //         console.log("Attempting Service Worker registration")
    //         navigator.serviceWorker.register("/service-worker.js").then(function(reg) {
    //             console.log("Service worker registered.", reg);
    //         }).catch((err) => console.log("Service Worker not registered.", err));
    //     });
    // }

    var deferredInstallPrompt = null;

    UserMenu.include({
        start: function() {
            window.addEventListener(
                "beforeinstallprompt",
                this.saveBeforeInstallPromptEvent
            );
            return this._super.apply(this, arguments);
        },
        saveBeforeInstallPromptEvent: function(evt) {
            deferredInstallPrompt = evt;
            try {
                this.$.find("#pwa_install_button")[0].removeAttribute("hidden");
            }
            catch (e) {
                console.log('[ServiceWorker] ERROR ', e);
            }
        },
        _onMenuInstallpwa: function() {
            deferredInstallPrompt.prompt();
            // Hide the install button, it can't be called twice.
            this.el.setAttribute("hidden", true);
            // Log user response to prompt.
            deferredInstallPrompt.userChoice.then(function(choice) {
                if (choice.outcome === "accepted") {
                    console.log("User accepted the A2HS prompt", choice);
                } else {
                    console.log("User dismissed the A2HS prompt", choice);
                }
                deferredInstallPrompt = null;
            });
        },
    });

    // ajax.jsonRpc("/bista_web_pwa/firebase/senderid", "call")
    //     .then(
    //         data => {
    //             if(data) {
    //                 console.log(data);
    //                 let firebaseConfig = {
    //                     messagingSenderId: String(data)
    //                 }
    //             }
    //         }
    //     )
    //     .catch(function(err) {
    //         console.log('---------err-------%r', err);
    //     });
});
