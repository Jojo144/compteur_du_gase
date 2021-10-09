#!/bin/bash


# Functions taken from https://github.com/YunoHost/yunohost on May, 28th, 2021.
# Changes are marked with #C#


#C# more complicated in real yunohost...
ynh_install_app_dependencies () {
    local dependencies=$@
    apt-get update
    apt-get install --yes $dependencies
}


#C# do nothing
ynh_app_setting_set () {
    :
}


#C# do nothing
ynh_webpath_available () {
    :
}



# Internal helper design to allow helpers to use getopts to manage their arguments
#
# [internal]
#
# example: function my_helper()
# {
#     local -A args_array=( [a]=arg1= [b]=arg2= [c]=arg3 )
#     local arg1
#     local arg2
#     local arg3
#     ynh_handle_getopts_args "$@"
#
#     [...]
# }
# my_helper --arg1 "val1" -b val2 -c
#
# usage: ynh_handle_getopts_args "$@"
# | arg: $@    - Simply "$@" to tranfert all the positionnal arguments to the function
#
# This helper need an array, named "args_array" with all the arguments used by the helper
# 	that want to use ynh_handle_getopts_args
# Be carreful, this array has to be an associative array, as the following example:
# local -A args_array=( [a]=arg1 [b]=arg2= [c]=arg3 )
# Let's explain this array:
# a, b and c are short options, -a, -b and -c
# arg1, arg2 and arg3 are the long options associated to the previous short ones. --arg1, --arg2 and --arg3
# For each option, a short and long version has to be defined.
# Let's see something more significant
# local -A args_array=( [u]=user [f]=finalpath= [d]=database )
#
# NB: Because we're using 'declare' without -g, the array will be declared as a local variable.
#
# Please keep in mind that the long option will be used as a variable to store the values for this option.
# For the previous example, that means that $finalpath will be fill with the value given as argument for this option.
#
# Also, in the previous example, finalpath has a '=' at the end. That means this option need a value.
# So, the helper has to be call with --finalpath /final/path, --finalpath=/final/path or -f /final/path, the variable $finalpath will get the value /final/path
# If there's many values for an option, -f /final /path, the value will be separated by a ';' $finalpath=/final;/path
# For an option without value, like --user in the example, the helper can be called only with --user or -u. $user will then get the value 1.
#
# To keep a retrocompatibility, a package can still call a helper, using getopts, with positional arguments.
# The "legacy mode" will manage the positional arguments and fill the variable in the same order than they are given in $args_array.
# e.g. for `my_helper "val1" val2`, arg1 will be filled with val1, and arg2 with val2.
#
# Requires YunoHost version 3.2.2 or higher.
ynh_handle_getopts_args () {
    # Manage arguments only if there's some provided
    set +o xtrace # set +x
    if [ $# -ne 0 ]
    then
        # Store arguments in an array to keep each argument separated
        local arguments=("$@")

        # For each option in the array, reduce to short options for getopts (e.g. for [u]=user, --user will be -u)
        # And built parameters string for getopts
        # ${!args_array[@]} is the list of all option_flags in the array (An option_flag is 'u' in [u]=user, user is a value)
        local getopts_parameters=""
        local option_flag=""
        for option_flag in "${!args_array[@]}"
        do
            # Concatenate each option_flags of the array to build the string of arguments for getopts
            # Will looks like 'abcd' for -a -b -c -d
            # If the value of an option_flag finish by =, it's an option with additionnal values. (e.g. --user bob or -u bob)
            # Check the last character of the value associate to the option_flag
            if [ "${args_array[$option_flag]: -1}" = "=" ]
            then
                # For an option with additionnal values, add a ':' after the letter for getopts.
                getopts_parameters="${getopts_parameters}${option_flag}:"
            else
                getopts_parameters="${getopts_parameters}${option_flag}"
            fi
            # Check each argument given to the function
            local arg=""
            # ${#arguments[@]} is the size of the array
            for arg in `seq 0 $(( ${#arguments[@]} - 1 ))`
            do
                # Escape options' values starting with -. Otherwise the - will be considered as another option.
                arguments[arg]="${arguments[arg]//--${args_array[$option_flag]}-/--${args_array[$option_flag]}\\TOBEREMOVED\\-}"
                # And replace long option (value of the option_flag) by the short option, the option_flag itself
                # (e.g. for [u]=user, --user will be -u)
                # Replace long option with = (match the beginning of the argument)
                arguments[arg]="$(echo "${arguments[arg]}" | sed "s/^--${args_array[$option_flag]}/-${option_flag} /")"
                # And long option without = (match the whole line)
                arguments[arg]="$(echo "${arguments[arg]}" | sed "s/^--${args_array[$option_flag]%=}$/-${option_flag} /")"
            done
        done

        # Read and parse all the arguments
        # Use a function here, to use standart arguments $@ and be able to use shift.
        parse_arg () {
            # Read all arguments, until no arguments are left
            while [ $# -ne 0 ]
            do
                # Initialize the index of getopts
                OPTIND=1
                # Parse with getopts only if the argument begin by -, that means the argument is an option
                # getopts will fill $parameter with the letter of the option it has read.
                local parameter=""
                getopts ":$getopts_parameters" parameter || true

                if [ "$parameter" = "?" ]
                then
                    ynh_die --message="Invalid argument: -${OPTARG:-}"
                elif [ "$parameter" = ":" ]
                then
                    ynh_die --message="-$OPTARG parameter requires an argument."
                else
                    local shift_value=1
                    # Use the long option, corresponding to the short option read by getopts, as a variable
                    # (e.g. for [u]=user, 'user' will be used as a variable)
                    # Also, remove '=' at the end of the long option
                    # The variable name will be stored in 'option_var'
                    local option_var="${args_array[$parameter]%=}"
                    # If this option doesn't take values
                    # if there's a '=' at the end of the long option name, this option takes values
                    if [ "${args_array[$parameter]: -1}" != "=" ]
                    then
                        # 'eval ${option_var}' will use the content of 'option_var'
                        eval ${option_var}=1
                    else
                        # Read all other arguments to find multiple value for this option.
                        # Load args in a array
                        local all_args=("$@")

                        # If the first argument is longer than 2 characters,
                        # There's a value attached to the option, in the same array cell
                        if [ ${#all_args[0]} -gt 2 ]
                        then
                            # Remove the option and the space, so keep only the value itself.
                            all_args[0]="${all_args[0]#-${parameter} }"

                            # At this point, if all_args[0] start with "-", then the argument is not well formed
                            if [ "${all_args[0]:0:1}" == "-" ]
                            then
                                ynh_die --message="Argument \"${all_args[0]}\" not valid! Did you use a single \"-\" instead of two?"
                            fi
                            # Reduce the value of shift, because the option has been removed manually
                            shift_value=$(( shift_value - 1 ))
                        fi

                        # Declare the content of option_var as a variable.
                        eval ${option_var}=""
                        # Then read the array value per value
                        local i
                        for i in `seq 0 $(( ${#all_args[@]} - 1 ))`
                        do
                            # If this argument is an option, end here.
                            if [ "${all_args[$i]:0:1}" == "-" ]
                            then
                                # Ignore the first value of the array, which is the option itself
                                if [ "$i" -ne 0 ]; then
                                    break
                                fi
                            else
                                # Ignore empty parameters
                                if [ -n "${all_args[$i]}" ]
                                then
                                    # Else, add this value to this option
                                    # Each value will be separated by ';'
                                    if [ -n "${!option_var}" ]
                                    then
                                        # If there's already another value for this option, add a ; before adding the new value
                                        eval ${option_var}+="\;"
                                    fi

                                    # Remove the \ that escape - at beginning of values.
                                    all_args[i]="${all_args[i]//\\TOBEREMOVED\\/}"

                                    # For the record.
                                    # We're using eval here to get the content of the variable stored itself as simple text in $option_var...
                                    # Other ways to get that content would be to use either ${!option_var} or declare -g ${option_var}
                                    # But... ${!option_var} can't be used as left part of an assignation.
                                    # declare -g ${option_var} will create a local variable (despite -g !) and will not be available for the helper itself.
                                    # So... Stop fucking arguing each time that eval is evil... Go find an other working solution if you can find one!

                                    eval ${option_var}+='"${all_args[$i]}"'
                                fi
                                shift_value=$(( shift_value + 1 ))
                            fi
                        done
                    fi
                fi

                # Shift the parameter and its argument(s)
                shift $shift_value
            done
        }

        # LEGACY MODE
        # Check if there's getopts arguments
        if [ "${arguments[0]:0:1}" != "-" ]
        then
            # If not, enter in legacy mode and manage the arguments as positionnal ones..
            # Dot not echo, to prevent to go through a helper output. But print only in the log.
            set -x; echo "! Helper used in legacy mode !" > /dev/null; set +x
            local i
            for i in `seq 0 $(( ${#arguments[@]} -1 ))`
            do
                # Try to use legacy_args as a list of option_flag of the array args_array
                # Otherwise, fallback to getopts_parameters to get the option_flag. But an associative arrays isn't always sorted in the correct order...
                # Remove all ':' in getopts_parameters
                getopts_parameters=${legacy_args:-${getopts_parameters//:}}
                # Get the option_flag from getopts_parameters, by using the option_flag according to the position of the argument.
                option_flag=${getopts_parameters:$i:1}
                if [ -z "$option_flag" ]
                then
                        ynh_print_warn --message="Too many arguments ! \"${arguments[$i]}\" will be ignored."
                        continue
                fi
                # Use the long option, corresponding to the option_flag, as a variable
                # (e.g. for [u]=user, 'user' will be used as a variable)
                # Also, remove '=' at the end of the long option
                # The variable name will be stored in 'option_var'
                local option_var="${args_array[$option_flag]%=}"

                # Store each value given as argument in the corresponding variable
                # The values will be stored in the same order than $args_array
                eval ${option_var}+='"${arguments[$i]}"'
            done
            unset legacy_args
        else
            # END LEGACY MODE
            # Call parse_arg and pass the modified list of args as an array of arguments.
            parse_arg "${arguments[@]}"
        fi
    fi
    set -o xtrace # set -x
}



# Print a message to stderr and exit
#
# usage: ynh_die --message=MSG [--ret_code=RETCODE]
# | arg: -m, --message=     - Message to display
# | arg: -c, --ret_code=    - Exit code to exit with
#
# Requires YunoHost version 2.4.0 or higher.
ynh_die() {
    # Declare an array to define the options of this helper.
    local legacy_args=mc
    local -A args_array=( [m]=message= [c]=ret_code= )
    local message
    local ret_code
    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"
    ret_code=${ret_code:-1}

    echo "$message" 1>&2
    exit "$ret_code"
}



# Exits if an error occurs during the execution of the script.
#
# usage: ynh_abort_if_errors
#
# This configure the rest of the script execution such that, if an error occurs
# or if an empty variable is used, the execution of the script stops immediately
# and a call to `ynh_clean_setup` is triggered if it has been defined by your script.
#
# Requires YunoHost version 2.6.4 or higher.
ynh_abort_if_errors () {
    set -o errexit  # set -e; Exit if a command fail
    set -o nounset  # set -u; And if a variable is used unset
#C#    trap ynh_exit_properly EXIT	# Capturing exit signals on shell script
}



# Substitute/replace a string (or expression) by another in a file
#
# usage: ynh_replace_string --match_string=match_string --replace_string=replace_string --target_file=target_file
# | arg: -m, --match_string=    - String to be searched and replaced in the file
# | arg: -r, --replace_string=  - String that will replace matches
# | arg: -f, --target_file=     - File in which the string will be replaced.
#
# As this helper is based on sed command, regular expressions and references to
# sub-expressions can be used (see sed manual page for more information)
#
# Requires YunoHost version 2.6.4 or higher.
ynh_replace_string () {
    # Declare an array to define the options of this helper.
    local legacy_args=mrf
    local -A args_array=( [m]=match_string= [r]=replace_string= [f]=target_file= )
    local match_string
    local replace_string
    local target_file
    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"

    local delimit=@
    # Escape the delimiter if it's in the string.
    match_string=${match_string//${delimit}/"\\${delimit}"}
    replace_string=${replace_string//${delimit}/"\\${delimit}"}

    sed --in-place "s${delimit}${match_string}${delimit}${replace_string}${delimit}g" "$target_file"
}




# Normalize the url path syntax
#
# [internal]
#
# Handle the slash at the beginning of path and its absence at ending
# Return a normalized url path
#
# examples:
#     url_path=$(ynh_normalize_url_path $url_path)
#     ynh_normalize_url_path example    # -> /example
#     ynh_normalize_url_path /example   # -> /example
#     ynh_normalize_url_path /example/  # -> /example
#     ynh_normalize_url_path /          # -> /
#
# usage: ynh_normalize_url_path --path_url=path_to_normalize
# | arg: -p, --path_url=    - URL path to normalize before using it
#
# Requires YunoHost version 2.6.4 or higher.
ynh_normalize_url_path () {
    # Declare an array to define the options of this helper.
    local legacy_args=p
    local -A args_array=( [p]=path_url= )
    local path_url
    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"

    test -n "$path_url" || ynh_die --message="ynh_normalize_url_path expect a URL path as first argument and received nothing."
    if [ "${path_url:0:1}" != "/" ]; then    # If the first character is not a /
        path_url="/$path_url"    # Add / at begin of path variable
    fi
    if [ "${path_url:${#path_url}-1}" == "/" ] && [ ${#path_url} -gt 1 ]; then    # If the last character is a / and that not the only character.
        path_url="${path_url:0:${#path_url}-1}"	# Delete the last character
    fi
    echo $path_url
}






# Check if a user exists on the system
#
# usage: ynh_system_user_exists --username=username
# | arg: -u, --username=    - the username to check
# | ret: 0 if the user exists, 1 otherwise.
#
# Requires YunoHost version 2.2.4 or higher.
ynh_system_user_exists() {
    # Declare an array to define the options of this helper.
    local legacy_args=u
    local -A args_array=( [u]=username= )
    local username
    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"

    getent passwd "$username" &>/dev/null
}



# Create a system user
#
# usage: ynh_system_user_create --username=user_name [--home_dir=home_dir] [--use_shell] [--groups="group1 group2"]
# | arg: -u, --username=    - Name of the system user that will be create
# | arg: -h, --home_dir=    - Path of the home dir for the user. Usually the final path of the app. If this argument is omitted, the user will be created without home
# | arg: -s, --use_shell    - Create a user using the default login shell if present. If this argument is omitted, the user will be created with /usr/sbin/nologin shell
# | arg: -g, --groups       - Add the user to system groups. Typically meant to add the user to the ssh.app / sftp.app group (e.g. for borgserver, my_webapp)
#
# Create a nextcloud user with no home directory and /usr/sbin/nologin login shell (hence no login capability) :
# ```
# ynh_system_user_create --username=nextcloud
# ```
# Create a discourse user using /var/www/discourse as home directory and the default login shell :
# ```
# ynh_system_user_create --username=discourse --home_dir=/var/www/discourse --use_shell
# ```
#
# Requires YunoHost version 2.6.4 or higher.
ynh_system_user_create () {
    # Declare an array to define the options of this helper.
    local legacy_args=uhs
    local -A args_array=( [u]=username= [h]=home_dir= [s]=use_shell [g]=groups= )
    local username
    local home_dir
    local use_shell
    local groups

    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"
    use_shell="${use_shell:-0}"
    home_dir="${home_dir:-}"
    groups="${groups:-}"

    if ! ynh_system_user_exists "$username"	# Check if the user exists on the system
    then	# If the user doesn't exist
        if [ -n "$home_dir" ]
        then	# If a home dir is mentioned
            local user_home_dir="--home-dir $home_dir"
        else
            local user_home_dir="--no-create-home"
        fi
        if [ $use_shell -eq 1 ]
        then	# If we want a shell for the user
            local shell="" # Use default shell
        else
            local shell="--shell /usr/sbin/nologin"
        fi
        useradd $user_home_dir --system --user-group $username $shell || ynh_die --message="Unable to create $username system account"
    fi

    local group
    for group in $groups
    do
        usermod -a -G "$group" "$username"
    done
}




# Display a message in the 'INFO' logging category
#
# usage: ynh_print_info --message="Some message"
# | arg: -m, --message=     - Message to display
#
# Requires YunoHost version 3.2.0 or higher.
ynh_print_info() {
    # Declare an array to define the options of this helper.
    local legacy_args=m
    local -A args_array=( [m]=message= )
    local message
    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"

    echo "$message" #C# >&$YNH_STDINFO
}



# Initial definitions for ynh_script_progression
increment_progression=0
previous_weight=0
max_progression=-1
# Set the scale of the progression bar
# progress_string(0,1,2) should have the size of the scale.
progress_scale=20
progress_string2="####################"
progress_string1="++++++++++++++++++++"
progress_string0="...................."
# Define base_time when the file is sourced
base_time=$(date +%s)


# Print a progress bar showing the progression of an app script
#
# usage: ynh_script_progression --message=message [--weight=weight] [--time]
# | arg: -m, --message= - The text to print
# | arg: -w, --weight=  - The weight for this progression. This value is 1 by default. Use a bigger value for a longer part of the script.
# | arg: -t, --time     - Print the execution time since the last call to this helper. Especially usefull to define weights. The execution time is given for the duration since the previous call. So the weight should be applied to this previous call.
# | arg: -l, --last     - Use for the last call of the helper, to fill the progression bar.
#
# Requires YunoHost version 3.5.0 or higher.
ynh_script_progression () {
    set +o xtrace # set +x
    # Declare an array to define the options of this helper.
    local legacy_args=mwtl
    local -A args_array=( [m]=message= [w]=weight= [t]=time [l]=last )
    local message
    local weight
    local time
    local last
    # Manage arguments with getopts
    ynh_handle_getopts_args "$@"
    # Re-disable xtrace, ynh_handle_getopts_args set it back
    set +o xtrace # set +x
    weight=${weight:-1}
    time=${time:-0}
    last=${last:-0}

    # Get execution time since the last $base_time
    local exec_time=$(( $(date +%s) - $base_time ))
    base_time=$(date +%s)

    # Compute $max_progression (if we didn't already)
    if [ "$max_progression" = -1 ]
    then
        # Get the number of occurrences of 'ynh_script_progression' in the script. Except those are commented.
        local helper_calls="$(grep --count "^[^#]*ynh_script_progression" $0)"
        # Get the number of call with a weight value
        local weight_calls=$(grep --perl-regexp --count "^[^#]*ynh_script_progression.*(--weight|-w )" $0)

        # Get the weight of each occurrences of 'ynh_script_progression' in the script using --weight
        local weight_valuesA="$(grep --perl-regexp "^[^#]*ynh_script_progression.*--weight" $0 | sed 's/.*--weight[= ]\([[:digit:]]*\).*/\1/g')"
        # Get the weight of each occurrences of 'ynh_script_progression' in the script using -w
        local weight_valuesB="$(grep --perl-regexp "^[^#]*ynh_script_progression.*-w " $0 | sed 's/.*-w[= ]\([[:digit:]]*\).*/\1/g')"
        # Each value will be on a different line.
        # Remove each 'end of line' and replace it by a '+' to sum the values.
        local weight_values=$(( $(echo "$weight_valuesA" | tr '\n' '+') + $(echo "$weight_valuesB" | tr '\n' '+') 0 ))

        # max_progression is a total number of calls to this helper.
        # 	Less the number of calls with a weight value.
        # 	Plus the total of weight values
        max_progression=$(( $helper_calls - $weight_calls + $weight_values ))
    fi

    # Increment each execution of ynh_script_progression in this script by the weight of the previous call.
    increment_progression=$(( $increment_progression + $previous_weight ))
    # Store the weight of the current call in $previous_weight for next call
    previous_weight=$weight

    # Reduce $increment_progression to the size of the scale
    if [ $last -eq 0 ]
    then
        local effective_progression=$(( $increment_progression * $progress_scale / $max_progression ))
    # If last is specified, fill immediately the progression_bar
    else
        local effective_progression=$progress_scale
    fi

    # Build $progression_bar from progress_string(0,1,2) according to $effective_progression and the weight of the current task
    # expected_progression is the progression expected after the current task
    local expected_progression="$(( ( $increment_progression + $weight ) * $progress_scale / $max_progression - $effective_progression ))"
    if [ $last -eq 1 ]
    then
        expected_progression=0
    fi
    # left_progression is the progression not yet done
    local left_progression="$(( $progress_scale - $effective_progression - $expected_progression ))"
    # Build the progression bar with $effective_progression, work done, $expected_progression, current work and $left_progression, work to be done.
    local progression_bar="${progress_string2:0:$effective_progression}${progress_string1:0:$expected_progression}${progress_string0:0:$left_progression}"

    local print_exec_time=""
    if [ $time -eq 1 ]
    then
        print_exec_time=" [$(date +%Hh%Mm,%Ss --date="0 + $exec_time sec")]"
    fi

    ynh_print_info "[$progression_bar] > ${message}${print_exec_time}"
    set -o xtrace # set -x
}
