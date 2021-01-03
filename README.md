check-flussonic
===============

Nagios/Icinga plugin to check flussonic state and monitor amount of alive streams. Problem is reported in case of flussonic general failure, or if % of alive streams less then configured.

Requirements
------------

Python 3.x

Usage
-----

Define command in icinga config:

```
object CheckCommand "check_flussonic_streams" {
	command = [ PluginDir + "/check-flussonic-streams.py" ]
        arguments = {
                "-H" = {
                        value = "$streamer_host$"
                        required = true
                        description = "host"
        		}
        		"-l" = {
        			value = "$api_user$"
        			required = false
        			description = "API Login"
        		}
        		"-p" = {
        			value = "$api_password$"
        			required = false
        			description = "API Password"
        		}
        		"--max_failed_streams_percent" = {
        			value = "$max_failed_streams_percent$"
        			required = false
        			description = "Max Failed Streams in percent"
        		}
        		"--timeout" = {
        			value = "$timeout$"
        			required = false
        			description = "HTTP Timeout"
        		}
		}
}
```

add it to your streamer hosts
```
template Host "flussonic" {
    import "generic-host"
    vars.streamer_host = name
    vars.api_user = "admin"
    vars.api_password = "password"
}

apply Service "flussonic_streams" {
	import "generic-service"
	check_command = "check_flussonic_streams"
	assign where host.vars.streamer_host
}

object Host "flussonic1.example.com" {
    import "flussonic"
    address = "flussonic1.example.com"
}
```