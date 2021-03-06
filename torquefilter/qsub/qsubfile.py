
import sys, re, getopt
from torquefilter.qsub.pbsattr import PBSattr

class qsubfile (PBSattr):
    "Class for PBS directives during job submission files"

    def parse_comm (self, line):
        """Strip lines designed as commands of file descriptors and/or shell
        piping characters"""

        processed_commands = []

        # Split line into terminated statements, then by pipe
        for statement in line.split (';'):
            for part in statement.split ('|'):
                # Remove patterns - <file.txt <<file.txt from start of command
                new = re.sub (r'^< ?[\w\.]*', '', part)
                new = re.sub (r'^>{1,2} ?[\w\.]*', '', new)
                # Remove pipeing commands from the end of the command
                new = re.sub (r'< ?[\w\.]*$', '', new)
                new = re.sub (r'>{1,2} ?[\w\.]*$', '', new)

                # Append command to list
                processed_commands.append (new.strip (' '))
        
        # Return all Commands
        return processed_commands

    def usage ( self ):
        """ Print qsub usage message if getopt Error occurs """

        sys.stderr.write ( "usage: qsub [-a data_time] [-A account_string] [-" )
        sys.stderr.write ( "b secs]\n\t[-c [ none | { enabled | periodic | " )
        sys.stderr.write ( "shutdown |\n\tdepth=<int> | dir=<path> | interva " )
        sys.stderr.write ( "l=<minutes>}... ]\n\t[-C directive_prefix] -d pa" )
        sys.stderr.write ( "th] [-D path]\n\t[-e path] [-h] [-I] [-j oe|eo|n]" )
        sys.stderr.write ( " [-k {oe}] [-l resource_list] [-m n|{abe}]\n\t" ) 
        sys.stderr.write ( "[-M user_list] [-N jobname] [-o path] [-p " )
        sys.stderr.write ( "priority] [-P proxy_user [-J <jobid]]\n\t" )
        sys.stderr.write ( "[-q queue] [-r y|n] [-S path] [-t number_to_" )
        sys.stderr.write ( "submit] [-T type] [-u user_list] [-w] path\n\t" )
        sys.stderr.write ( "[-W additional_attributes] [-v variable_list]" )
        sys.stderr.write ( " [-V] [-x] [-X] [-z] [script]\n\n" )

    def commline (self, args):
        "Wrapper for parseOpts for CLI options"

        return self.parseOpts (args, overWrite=True)

    def parseOpts (self, options, overWrite=False):
        """Parse options list, sending each value to the correct PBSattr
        method"""

        # Map datatype to store locally (allowing for duplication)
        tmp_attr = { }

        qsub_opts = "zXxVIhfna:A:b:c:C:d:D:e:j:k:l:m:M:N:o:p:P:q:r:S:t:T:u:v:w:W:"

        opts, args = getopt.gnu_getopt (options, qsub_opts)
            
        for o, a in opts:
            if o in ("-q"):
                tmp_attr ['queue'] = a
            elif o in ("-l"):
                # Parse resource into mapping attribute
                for type in a.split (','):
                    # Add extra split for nodes resource and it's respective
                    # properties
                    if 'nodes' in type:
                        for each in type.split (':'):
                            if ('=' in each):
                                keyword, value = each.split ('=')
                                tmp_attr [keyword] = value
                            else:
                                tmp_attr [each] = True
                    else:
                        # All other resources
                        if ('=' in type):
                            keyword, value = type.split ('=')
                            tmp_attr [keyword] = value
                        else:
                            tmp_attr [type] = True
            elif o in ("-I"):
                tmp_attr ['Interactive'] = True
            else:
                continue

        # Now send mapping structure to PBS attr to add to global file class
        PBSattr.add_attr (self, tmp_attr, overWrite)

        return args


    def processfile ( self, fn, printfile = True, outfile = False ):
        """Scan qsub file (or STDIN) identifing PBS directives or commands and
        process according."""


        if ( 'STDIN' == fn ):
            input = sys.stdin
        else:
            input = open ( fn, 'r' )

        args = [ ]
        parse_directives = True

        # Setup outfile if any
        if ( outfile ):
            output = open ( outfile, 'w' )
        else:
            output = sys.stdout

        for line in input:
            # Make sure submit script echoed to STDOUT for qsub command
            if ( printfile ):
                output.write ( line )
            # Skip empty lines or lines with only whitespace
            if ( re.match ( r'^\s*$', line ) ):
                continue;

            line = line.strip ( '\n' )
            if ( line.startswith ( '#' ) ):
                if ( line.startswith ( '#PBS ' ) ):
                    if ( parse_directives ):
                        for directive in line.lstrip ( '#PBS ' ).split ( ' ' ):
                            args.append ( directive )
            else:
                if ( parse_directives ):
                    parse_directives = False
                for each in self.parse_comm ( line ):
                    PBSattr.add_command ( self, each )

        # Parse Options in correct order
        self.parseOpts ( args )

        if ( outfile ):
            output.close ()
        input.close ()
               
