vcdapi_docset
=============

A docset generator for the [VMware vCloud Director][http://www.vmware.com/products/vcloud-director] REST API.

The docset can be used with [Dash][http://kapeli.com/dash]


## Requirements
Uses python and [scrapy][http://scrapy.org] to download the documentation files and generate the docset.
Run `scrapy crawl vcd_api` inside the root directory to generate the docset.


## Notes
Does not pull down some of the ancillary html files, these have been manually downloaded and included in the docset (e.g. `doc-style.css`, `right-pane.html`).
Does not tar the package on completion.  The tar'd docset has been included for convenience.