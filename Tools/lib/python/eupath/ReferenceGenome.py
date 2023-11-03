#!/usr/bin/python

from . import EupathExporter
import re


class Genome:

    def __init__(self, reference_genome):
        """
        reference_genome is a string parameter, from a pulldown list provided by VEuPathDB.  
        It should be of the form: PROJECTID-BUILDNUM_STRAINNAME_Genome
        This method parses the string, to provide the info in a structured object.
        :param reference_genome: the reference genome parameter provided by the user

        raise exception if not valid ref genome string
        """

        # Insure the the reference genome matches the pattern for Eupath originated reference genomes.
        if not reference_genome or not re.match(r'^.+-\d+_.+_Genome$', reference_genome, flags=0):
            raise Exception("Invalid genome string")
        self._identifier = reference_genome
        self._project = reference_genome[0:reference_genome.index("-")]
        sans_project = reference_genome[reference_genome.index("-") + 1:]
        components = sans_project.split("_")
        self._version = components[0]
        self._display_name = components[1] + " Genome"

    @property
    def project(self):
        return self._project

    @property
    def version(self):
        return self._version

    @property
    def display_name(self):
        return self._display_name

    @property
    def identifier(self):
        return self._identifier
