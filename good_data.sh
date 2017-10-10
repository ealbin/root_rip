#!/bin/bash
egrep -v ' to 2015|beta| 0 / ' data_summary | egrep ' [0-9]{3,} / |==|model'
