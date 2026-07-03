/* CITE Helpdesk — portal form /citehelpdesk2/new.
   Validates a maximum of 5 attachment files. (Location now applies across all
   companies and Sub Category is hidden, so there are no more dependent
   dropdowns on the portal.) */
(function () {
    "use strict";

    var MAX_FILES = 5;

    document.addEventListener("DOMContentLoaded", function () {
        var form = document.getElementById("cite_ticket_form");
        if (!form) {
            return;
        }
        var fileInput = document.getElementById("cite_attachments");
        if (fileInput) {
            fileInput.addEventListener("change", function () {
                if (fileInput.files && fileInput.files.length > MAX_FILES) {
                    alert(
                        "Maximum " + MAX_FILES +
                        " attachments. Please select again."
                    );
                    fileInput.value = "";
                }
            });
        }
    });
})();
