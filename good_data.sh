#!/bin/bash
egrep -v ' to 2015|beta|6.1-bat| 0 / ' data_summary | egrep ' [0-9]{3,} / |==|model' | egrep -v '\[( *[0-9]{1,2}| *[0-9]{4,}| *-.*)\]'
