from . import EupathExporter
from . import ReferenceGenome
import sys

class GeneListExporter(EupathExporter.Exporter):

    GENE_LIST_TYPE = "GeneList"
    GENE_LIST_VERSION = "1.0"
    UNSPECIFIED_REF_GENOME_KEY = "?"

    def initialize(self, stdArgsBundle, typeSpecificArgsList):

        super().initialize(stdArgsBundle, GeneListExporter.GENE_LIST_TYPE, GeneListExporter.GENE_LIST_VERSION)

        ##  TODO:  make this 2
        if len(typeSpecificArgsList) != 3: 
            print("The tool was passed an insufficient numbers of arguments.", file=sys.stderr)
            exit(1)

        # Override the dataset genome reference with that provided via the form.
        # (We need a ref genome in order to decide which project the gene list is for.  BUT... a gene list might
        # contain genes from mulitple genomes)
        refGenomeKey = typeSpecificArgsList[0]
        if len(refGenomeKey.strip()) == 0 or refGenomeKey == GeneListExporter.UNSPECIFIED_REF_GENOME_KEY:
            print("Please select a reference genome from the provided list.", file=sys.stderr)
            exit(1);
        self._genome = ReferenceGenome.Genome(refGenomeKey)
        self._dataset_file_path = typeSpecificArgsList[1]
        self._dataset_file_name = typeSpecificArgsList[2]

    def identify_dependencies(self):
        """
        The appropriate dependency(ies) will be determined by the reference genome selected - only one for now
        The EuPathDB reference genomes will have a project id, a EuPath release number, and a genome description
        all separated by a dash in the first instance and an underscore in the second instance.
        :return: list containing the single dependency with the component parts parsed out (only one for now)
        """
        return [{
            "resourceIdentifier": self._genome.identifier,
            "resourceVersion": self._genome.version,
            "resourceDisplayName": self._genome.display_name
        }]

    def identify_projects(self):
        """
        The appropriate project(s) will be determined by the reference genome selected - only one for now
        The project name must be listed in the SUPPORTED_PROJECTS array.  Failure to find it will be
        regarded as a validation exception.
        :return: list containing the single relevant EuPath project (only one for now)
        """
        return [self._genome.project]

    def identify_dataset_files(self):
        """
        The user provided gene list file is combined with the name EuPathDB expects
        for such a file
        :return: A list containing the single dataset file accompanied by its EuPathDB designation.
        """
        return [{"name": self._dataset_file_name, "path": self._dataset_file_path}]
