from . import EupathExporter
from . import ReferenceGenome
import sys
import json
import os
import re

class RnaSeqExporter(EupathExporter.Exporter):

    """
INPUT
    type specific args:  
      a list of tuples. 

    tuple format is: [filepath, samplename, refgenome_key, suffix]

    suffixes provided by the galaxy UI are either 'bw' or 'txt' (for fpkm or tpm files)
    
OUTPUT
  files are given cannonical names:
     sample.suffix (with sample name cleaned of icky characters)

  manifest.txt file with one line per tuple:
    for txt file:
      samplename filename strandinfo 
    for bw file:
      samplename filename strandinfo 

    (strandinfo will always be 'unstranded'.  we no longer support sense/antisense.)

  dependency info:
   - reference genome and version (unanimous consensus of the samples provided)

NOTE: we retain mention of 'stranded' for backward compatability.  The Exporter previously attempted (badly) to accommodate sense/antisense, which has been removed.

SEE VDI IMPORTER FOR VALIDATION RULES

    """
    
    # Name given to this type of dataset and to the expected file
    TYPE = "RNASeq"
    VERSION = "1.0"

    def initialize(self, stdArgsBundle, typeSpecificArgsList):

        super().initialize(stdArgsBundle, RnaSeqExporter.TYPE, RnaSeqExporter.VERSION)

        if len(typeSpecificArgsList) < 4:
            print("The tool was passed an insufficient numbers of arguments.", file=sys.stderr)
            exit(1)

        if len(typeSpecificArgsList) % 4 != 0:
            print("Invalid number of arguments.  Must be one or more 4-tuples.", file=sys.stderr)
            exit(1)


        # grab ref genome from first tuple.  all others must agree
        self._refGenomeKey = typeSpecificArgsList[2]
        try:
            self._refGenome = ReferenceGenome.Genome( self._refGenomeKey)
        except:
            print("All input datasets must have valid, and identical, reference genomes", file=sys.stderr)
            exit(1)

        self._datasetInfos = []

        # open manifest file for writing
        manifestPath = "/tmp/manifest." + str(os.getpid()) + ".txt"
        manifest = open(manifestPath, "w+")

        # process variable number of [filepath, samplename, refgenome_key, suffix] tubles
        fileNumber = 0
        for i in range(0, len(typeSpecificArgsList), 4):   # increment by tuple size (4)
            
            # print >> sys.stderr, "args[" + str(i) + "] = " + args[i]
            path = typeSpecificArgsList[i+0]
            samplename = typeSpecificArgsList[i+1]
            refGenomeKey = typeSpecificArgsList[i+2]
            suffix = typeSpecificArgsList[i+3]

            if refGenomeKey != self._refGenomeKey:
                print("All datasets must have the same reference genome identifier and version. Sample " + samplename + " does not agree with the others: " + refGenomeKey, file=sys.stderr)
                exit(1)
            
            filename = self.clean_file_name(re.sub(r"\s+", "_", samplename) + "." + suffix)

            fileNumber += 1
            strandedness = "unstranded"

            self._datasetInfos.append({"name": filename, "path": path})
            print(samplename + "\t" + filename + "\t" + strandedness, file=manifest)

        manifest.close()
        self._datasetInfos.append({"name": "manifest.txt", "path": manifestPath})

        # print >> sys.stderr, "datasetInfos: " + json.dumps(self._datasetInfos) + "<<- END OF datasetInfos"

    def identify_dependencies(self):
        """
        The appropriate dependency(ies) will be determined by the reference genome selected - only one for now
        """
        return [{
            "resourceIdentifier": self._refGenome.identifier,
            "resourceVersion": self._refGenome.version,
            "resourceDisplayName": self._refGenome.display_name
        }]

    def identify_projects(self):
        return [self._refGenome.project]

    def identify_dataset_files(self):
        """
        :return: A list containing the dataset files accompanied by their VEuPathDB designation.
        """
        return self._datasetInfos
