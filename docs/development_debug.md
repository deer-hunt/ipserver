# Development and Debugging

## Overview

This description is description of development and debugging related `ipserver`.

## Program specification

| **Item**          | **Description**            |
|-------------------|-----------------------|
| **Python version**| 3.0 or later. * |
| **Dependencies**   | multipart              |


## Related documents

- [Customizing and Examples(.md)](./customize_examples.md)


## Debugging

You can see detailed debug information by specifying `--verbose=3` or `--debug`. In detail, please read `--verbose` option.

```bash
$ ipserver ***** --verbose=2    #INFO
$ ipserver ***** --verbose=3    #DEBUG

$ ipserver ***** --info     #INFO  This option is equivalent to "--verbose=2"

$ ipserver ***** --debug     #DEBUG  This option is equivalent to "--verbose=3"
```


### Log sample and description

The following is debugging log with each comments.



## Not support Python 2.7 ?

"ipserver" doesn't support Python 2.7. However "ipserver" has been developed to avoid using the latest Python specifications as much as possible, So you can refactor to Python 2.7 code easily.

**Refactoring points**

- ABC module
- http.client module
- urllib module

> And any other few modules.

