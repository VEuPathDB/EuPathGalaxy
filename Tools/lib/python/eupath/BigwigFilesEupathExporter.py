from . import EupathExporter
from . import ReferenceGenome
import sys
import os

class BigwigFilesExporter(EupathExporter.Exporter):
    """
INPUT
    type specific args:  
      - user's explicit choice of a ref genome key (a string encoding project, buildnum, genome)
      - one or more tuples of: [filepath, filename, ref_genome_key]
        - ref_genome_key must be "Unspecified(?)" or agree with explicit ref genome key. else error. 
        - all files must have .bw type

OUTPUT
  files given cannonical names:
     if file extension is .bw, no change
     if file extension is .bigwig, replace with .bw
     otherwise append .bw

  dependency info:
   - reference genome and version (as specified in dedicated ref genome parameter)
    """

    # Constants
    TYPE = "BigwigFiles"
    VERSION = "1.0"
    UNSPECIFIED_REF_GENOME_KEY = "?"

    def initialize(self, stdArgsBundle, typeSpecificArgsList):

        super().initialize(stdArgsBundle, BigwigFilesExporter.TYPE, BigwigFilesExporter.VERSION)

        if len(typeSpecificArgsList) < 4:
            print("The tool was passed an insufficient numbers of arguments.", file=sys.stderr)
            exit(1)

        if (len(typeSpecificArgsList) - 1) % 3 != 0:
            print("Invalid number of arguments.  Must be a reference genome followed by one or more 3-tuples.", file=sys.stderr)
            exit(1)

        ## list arguments (for debuging)  (these can easily be seen in the galaxy UI)
        # print("args to BigwigFilesEupathExporter.py", file=sys.stderr)
        # for i in range(0, len(typeSpecificArgsList)):
        #     print(str(typeSpecificArgsList[i]), file=sys.stderr)

        self._refGenomeKey = typeSpecificArgsList[0]
        if len(self._refGenomeKey.strip()) == 0 or self._refGenomeKey == BigwigFilesExporter.UNSPECIFIED_REF_GENOME_KEY:
            print("Please select a reference genome from the provided list.", file=sys.stderr)
            exit(1);

        try:    
            self._refGenome = ReferenceGenome.Genome(self._refGenomeKey)
        except:
            print("Please provide a valid reference genome", file=sys.stderr)
            exit(1)

        self._datasetInfos = []
        
        # process variable number of [dataset refgenome] pairs.
        # confirm that all dataset provided ref genomes are identical.
        for i in range(1, len(typeSpecificArgsList), 3):    # start after ref genome arg, increment by tuple size (3)

            path = typeSpecificArgsList[i+0]
            filename = typeSpecificArgsList[i+1]  # user's original file name
            refGenomeKey = typeSpecificArgsList[i+2]

            # check file suffix (and set if needed)
            if filename.endswith(".bigwig"):
                filename = filename[0:-6] + "bw"
            elif not filename.endswith(".bw"):
                filename = filename + ".bw"

            # check file size
            size = os.stat(path).st_size
            sizeLimit = 500 * 1024 * 1024 # 500MB
            # print >> sys.stderr, "file size is " + str(size)
            if size > sizeLimit:
                print("File exceeds 500MB size limit: " + filename, file=sys.stderr)
                exit(1)

            if refGenomeKey != BigwigFilesExporter.UNSPECIFIED_REF_GENOME_KEY and refGenomeKey != self._refGenomeKey:
                print("File " + filename + " is annotated with ref genome " + refGenomeKey + " which conflicts with what you specified for the export: " + self._refGenomeKey, file=sys.stderr)
                exit(1)

            self._datasetInfos.append({"name": filename, "path": path})

        # for testing
        # sys.exit(1)

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
