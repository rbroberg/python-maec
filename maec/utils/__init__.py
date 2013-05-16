#MAEC Utility Methods

#Copyright (c) 2013, The MITRE Corporation
#All rights reserved.

#Compatible with MAEC v4.0
#Last updated 5/16/2013

"""MAEC utility methods"""

from cybox.utils import NamespaceParser, OBJECT_TYPES_DICT

import itertools

class MAECNamespaceParser(NamespaceParser):
    superclass = NamespaceParser
    def __init__(self, bundle = None, package = None):
        super(MAECNamespaceParser, self).__init__([])
        self.bundle = bundle
        self.package = package
        self.process_namespaces()

    def process_namespaces(self):
        if self.package is not None: self.process_package_namespace(self.package)
        elif self.bundle is not None: self.process_bundle_namespace(self.bundle)

    def process_package_namespace(self, package):
        if self.package.get_Malware_Subjects() is not None:
            for malware_subject in self.package.get_Malware_Subjects().get_Malware_Subject():
                if malware_subject.get_Malware_Instance_Object_Attributes() is not None:
                    self.get_namespace_from_object(malware_subject.get_Malware_Instance_Object_Attributes())
                if malware_subject.get_Findings_Bundles() is not None:
                    for bundle in malware_subject.get_Findings_Bundles().get_Bundle():
                        self.process_bundle_namespace(bundle)

    def process_bundle_namespace(self, bundle):
        if bundle.get_Malware_Instance_Object_Attributes() is not None:
            self.get_namespace_from_object(self.bundle.get_Malware_Instance_Object_Attributes())
        if bundle.get_Process_Tree() is not None:
            self.add_object_namespace('ProcessObjectType')
        if bundle.get_Behaviors() is not None:
            for behavior in bundle.get_Behaviors().get_Behavior():
                self.process_behavior_namespace(self, behavior)
        if bundle.get_Actions() is not None:
            for action in bundle.get_Actions().get_Action():
                self.process_action_namespace(action)
        if bundle.get_Objects() is not None:
            for object in bundle.get_Objects().get_Object():
                self.get_namespace_from_object(object)
        if bundle.get_Collections() is not None:
            collections = bundle.get_Collections()
            if collections.get_Behavior_Collections() is not None:
                for behavior_collection in collections.get_Behavior_Collections().get_Behavior_Collection():
                    if behavior_collection.get_Behavior_List() is not None:
                        for behavior in behavior_collection.get_Behavior_List().get_Behavior():
                            self.process_behavior_namespace(behavior)
            if collections.get_Action_Collections() is not None:
                for action_collection in collections.get_Action_Collections().get_Action_Collection():
                    if action_collection.get_Action_List() is not None:
                        for action in action_collection.get_Action_List().get_Action():
                            self.process_action_namespace(action)
            if collections.get_Object_Collections() is not None:
                for object_collection in collections.get_Object_Collections().get_Object_Collection():
                    if object_collection.get_Object_List() is not None:
                        for object in object_collection.get_Object_List().get_Object():
                            self.get_namespace_from_object(object)

    def process_behavior_namespace(self, behavior):
        if behavior.get_Action_Composition() is not None:
            for action in behavior.get_Action_Composition().get_Action():
                self.process_action_namespace(action)

    def process_action_namespace(self, action):
        if action.get_Associated_Objects() is not None:
            for associated_object in action.get_Associated_Objects().get_Associated_Object():
                self.get_namespace_from_object(associated_object)
   
    def build_maec_namespaces_schemalocations_str(self):
        '''Build the namespace/schemalocation declaration string'''
        
        output_string = '\n '
        schemalocs = []
        #Add the XSI, MAEC, and CybOX Core/Common namespaces and schemalocation
        output_string += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n '
        if self.package is not None:
            output_string += 'xmlns:maecPackage="http://maec.mitre.org/XMLSchema/maec-package-2" \n '
            output_string += 'xmlns:maecBundle="http://maec.mitre.org/XMLSchema/maec-bundle-4" \n '
            output_string += 'xmlns:mmdef="http://xml/metadataSharing.xsd" \n '
            schemalocs.append('http://maec.mitre.org/XMLSchema/maec-package-2 http://maec.mitre.org/language/version4.0/maec_package_schema.xsd')
        elif self.bundle is not None:
            output_string += 'xmlns:maecBundle="http://maec.mitre.org/XMLSchema/maec-bundle-4" \n '
            output_string += 'xmlns:mmdef="http://xml/metadataSharing.xsd" \n '
            schemalocs.append('"http://maec.mitre.org/XMLSchema/maec-bundle-4 http://maec.mitre.org/language/version4.0/maec_bundle_schema.xsd')
        output_string += 'xmlns:cybox="http://cybox.mitre.org/cybox-2" \n '
        output_string += 'xmlns:cyboxCore="http://cybox.mitre.org/common-2" \n '
        schemalocs.append(' http://cybox.mitre.org/cybox-2 http://cybox.mitre.org/XMLSchema/core/2.0/cybox_core.xsd')
        
        for object_type in self.object_types:
            namespace_prefix = OBJECT_TYPES_DICT.get(object_type).get('namespace_prefix')
            namespace = OBJECT_TYPES_DICT.get(object_type).get('namespace')
            output_string += ('xmlns:' + namespace_prefix + '=' + '"' + namespace + '"' + ' \n ')
        
        for object_type_dependency in self.object_type_dependencies:
            if object_type_dependency not in self.object_types:
                namespace_prefix = OBJECT_TYPES_DICT.get(object_type_dependency).get('namespace_prefix')
                namespace = OBJECT_TYPES_DICT.get(object_type_dependency).get('namespace')
                output_string += ('xmlns:' + namespace_prefix + '=' + '"' + namespace + '"' + ' \n ')
        
        output_string += 'xsi:schemaLocation="'
        
        for object_type in self.object_types:
            namespace = OBJECT_TYPES_DICT.get(object_type).get('namespace')
            schemalocation = OBJECT_TYPES_DICT.get(object_type).get('schemalocation')
            schemalocs.append(' ' + namespace + ' ' + schemalocation)
        
        for schemalocation_string in schemalocs:
            if schemalocs.index(schemalocation_string) == (len(schemalocs) - 1):
                output_string += (schemalocation_string + '"')
            else:
                output_string += (schemalocation_string + '\n')
        
        return output_string
    

