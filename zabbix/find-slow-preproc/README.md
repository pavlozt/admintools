# Profiling zabbix preprocessors

How to identify slow preprocessing items in zabbix server or zabbix proxy.
This method allows you to avoid debug logs and reduce the overhead of it.

 1. First, you need install bpftrace tool (https://github.com/iovisor/bpftrace/blob/master/INSTALL.md)
 2. Run script `zbx_preproc_histogram.bt` to get call time histogram and idenitify your filter value.

    Output may looks like (this is log2 histogram):
    ```
    ./zbx_preproc_hist.bt
    Attaching 4 probes...
    Making delay historgram of zabbix preprocessors... Hit Ctrl-C to end.
    ^C
    @usecs:
    [1]                    8 |                                                    |
    [2, 4)                51 |@@@                                                 |
    [4, 8)               667 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
    [8, 16)              643 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  |
    [16, 32)              28 |@@                                                  |
    [32, 64)               2 |                                                    |
    [64, 128)              1 |                                                    |
    ```

    This is μsec units - microseconds, 1/1000000 of second.

    If you do not observe high segments of the histogram during your polling cycle, more than 1024, you can stop here.

 3. Run script and wait until it starts displaying zabbix item identifiers.
    For example, if you select  10 ms limit, you need run :
    ```
    ./zbx_show_pp_slow.bt 1000
    ```
    This run will produce output like this:
    ```
    Attaching 4 probes...
    Tracing Zabbix preprocessors with limit 1000 usecs.. Hit Ctrl-C to end.
    delay 1137 us, item 47362
    delay 1253 us, item 47841
    ```
 4. Go to zabbix web interface, "Latest data" menu and display history of any item to get url
   i.e.  `https://.../history.php?action=showgraph&itemids[]=123456`

 5. Change item id in browser URL and load this page. This page show item name and graph for item.

This procedure typically results id of complex dependent items, so the value will often be empty, but you have many other dependent items.

Usually loaded Zabbix installations use a zabbix_proxy for preprocessing.
If you use Zabbix server without zabbix_proxy, you should modify scripts and change program name `zabbix_proxy` in probe string:
```
  uprobe:/usr/sbin/zabbix_proxy:zbx_preprocess_item_value
```
