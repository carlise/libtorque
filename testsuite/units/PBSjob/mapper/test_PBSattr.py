
#!/bin/env python
# Test PBSattr Class


import unittest

from torquefilter.PBSjob.mapper.pbsattr import PBSattr

class Test_PBS_map(unittest.TestCase):

    def setUp(self):
        self.current = PBSattr()

    def test_map_attribute(self):
        "Check that attributes can be mapped"

        map_attr = {}
        map_attr['queue'] = "standby"
        self.current.add_attribute(map_attr)
        self.assertEqual(self.current.attributes['queue'], "standby")

    def test_no_overwrite_attribute(self):
        "Check that duplicates do not overwrite initial attribute by default"

        map_attr = {}
        second_attr = {}
        map_attr['queue'] = "standby"
        second_attr['queue'] = "comm_mmem_week"
        self.current.add_attribute(map_attr)
        self.current.add_attribute(second_attr)
        self.assertEqual(self.current.attributes['queue'], "standby")

    def test_overwrite_attribute(self):
        "Check that duplicates overwrite initial attribute if configured"

        map_attr = {}
        second_attr = {}
        map_attr['queue'] = "standby"
        second_attr['queue'] = "comm_mmem_week"
        self.current.add_attribute(map_attr)
        self.current.add_attribute(second_attr, overWrite=True)
        self.assertEqual(self.current.attributes['queue'], "comm_mmem_week")

    def test_map_multiple_attribute(self):
        "Check that multiple attributes can be mapped at the same time"

        map_attr = {}
        map_attr['queue'] = "standby"
        map_attr['nodes'] = "1"
        map_attr['pvmem'] = "5GB"
        map_attr['ppn'] = "1"
        self.current.add_attribute(map_attr)
        self.assertEqual(self.current.attributes['pvmem'], "5GB")
        self.assertEqual(self.current.attributes['nodes'], "1")

    def test_map_command(self):
        "Check that commands can be mapped"

        self.current.add_command("ssh srih0001")
        self.assertEqual(['ssh', 'srih0001'], self.current.commands[0])

    def test_command_index(self):
        "Check that we can reference specific indexes of mapped commands"

        self.current.add_command("ssh srih0001")
        self.current.add_command("qsub -N file")
        self.assertEqual(self.current.commands[1], ['qsub', '-N', 'file'])
        self.assertEqual(self.current.commands[1][0], 'qsub')

    def test_map_resource_list(self):
        "Check that resource_list attributes are mapped correctly"

        map_attr = {}
        map_attr['resource_list'] = [['nodes=1:ppn=3'],['pvmem=5gb']]
        self.current.add_attribute(map_attr)

        self.assertEqual(self.current.attributes['pvmem'], '5gb')
        self.assertEqual(self.current.attributes['nodes'], '1')
        self.assertEqual(self.current.attributes['ppn'], '3')
        

if __name__ == '__main__':
    unittest.main()