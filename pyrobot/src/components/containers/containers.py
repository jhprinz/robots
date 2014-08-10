'''
Created on 07.05.2014

@author: jan-hendrikprinz
'''

################################################################################
##  PLATE TYPE DATABASE
################################################################################

import numpy as np
from components.containers.containerfactory import ContainerFactory
from components.containers.wellsutils import WellUtils

from simplemysql import SimpleMysql 

class Container(ContainerFactory, WellUtils):
    
    _db = None
    _xml = None

    @staticmethod
    def connect_mysql():
        Container._db = SimpleMysql(
            host="localhost",
            db="platetype",
            user="plate",
            passwd="plate",
            keep_alive=True # try and reconnect timedout mysql connections?
        )
        
    @staticmethod
    def connect_xml(filename = None):
        if filename is None:
            filename = 'platetypes.xml'

        s = ''
        with open (filename, "r") as myfile:
            s = myfile.read()   

        Container._xml = s
            
    def __init__(self, *initial_data, **kwargs):
        
        self.id = 0

        # These should have been autogenerated from the docstring in definition.md
        
        self.general_id = ''
        self.general_checked = False
        self.general_name = ''
        self.general_name_short = ''
        self.general_description = ''
        self.general_comment = ''
        self.general_image = ''
        self.manufacturer_name = ''
        self.manufacturer_url = ''
        self.manufacturer_product_url = ''
        self.manufacturer_number = ''
        self.manufacturer_pdf_url = ''
        self.id_momentum = ''
        self.id_evo = ''
        self.id_infinite = ''
        self.id_barcode = ''
        self.plate_color = 'black'
        self.plate_material = ''
        self.plate_rows = 8
        self.plate_columns = 12
        self.plate_numbering = 'row'
        self.plate_height = 14.4
        self.plate_length = 127.76
        self.plate_width = 85.48
        self.plate_sterile = False
        self.flange_type = ''
        self.flange_width = 0.0
        self.stacking_above = True
        self.stacking_below = True
        self.stacking_plate_height = 0.0
        self.well_size = 'full'
        self.well_coating = 'none) (free'
        self.well_shape = 'round'
        self.well_bottom = ''
        self.well_profile = 'flat'
        self.well_profile_anlge = '30.0'
        self.well_diameter_bottom_x = 0.0
        self.well_diameter_bottom_y = 0.0
        self.well_diameter_top_x = 0.0
        self.well_diameter_top_y = 0.0
        self.well_position_first_x = 0.0
        self.well_position_first_y = 0.0
        self.well_distance_x = 0.0
        self.well_distance_y = 0.0
        self.well_depth = 0.0
        self.well_volume_max = 0.0
        self.well_volume_working_min = 0.0
        self.well_volume_working_max = 0.0
        self.lid_allowed = True
        self.lid_offset = 0.0
        self.lid_plate_height = 0.0
        self.momentum_grip_force = 0
        self.momentum_offsets_low_lidded_plate = 0.0
        self.momentum_offsets_high_lidded_plate = 0.0
        self.momentum_offsets_custom_lidded_plate = 0.0
        self.momentum_offsets_low_lidded_lid = 0.0
        self.momentum_offsets_high_lidded_lid = 0.0
        self.momentum_offsets_custom_lidded_lid = 0.0
        self.momentum_offsets_low_grip_transform = 'Identity'
        self.momentum_offsets_high_grip_transform = 'Identity'
        self.momentum_offsets_custom_grip_transform = 'Identity'
        self.evo_plate_grip_force = 75
        self.evo_lid_grip_force = 60
        self.evo_lid_grip_narrow = 92.0
        self.evo_lid_grip_wide = 135.0
        
        for dictionary in initial_data:
            for key in dictionary:
                if key != '':
                    setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])   

    @property
    def plate_bottom_read (self):
        if self.well_bottom != 'solid':
            plate_bottom_read = True
        else:
            plate_bottom_read = False

        return plate_bottom_read

    @property
    def well_position_last_x (self):
        well_position_last_x = self.well_position_first_x + self.plate_columns * self.well_distance_x
        return well_position_last_x
    
    @property
    def well_position_last_y (self):
        well_position_last_y = self.well_position_first_y + self.plate_rows * self.well_distance_y
        return well_position_last_y    
    
    @property
    def plate_type (self):
        plate_type = int(self.plate_rows) * int(self.plate_columns)
        return plate_type
    
    @property
    def stacking_plate_shift (self):
        stacking_plate_shift = self.plate_height - self.stacking_plate_height 
        return stacking_plate_shift

    @property        
    def flange_height_short(self):
        flange_heights_shortside = { 'short' : 2.41, 'medium' : 6.10, 'tall' : 7.62, 'interrupted' : 2.41, 'dual' : 2.41}
        
        if self.flange_type in flange_heights_shortside:
            return flange_heights_shortside[self.flange_type]
        else:
            # use maximum to be on the safe side
            return 7.62
    @property
    def flange_height_long(self):
        flange_heights_longside = { 'short' : 2.41, 'medium' : 6.10, 'tall' : 7.62, 'interrupted' : 6.85, 'dual' : 7.62}
        
        if self.flange_type in flange_heights_longside:
            return flange_heights_longside[self.flange_type]
        else:
            # use maximum to be on the safe side
            return 7.62
                    
    @property
    def flange_dropstage(self, side='N'):
        if side == 'N' or side == 'S':
            return self.flange_height_long > 3.00
        else:
            return self.flange_height_short > 3.00
        
    @staticmethod
    def _from(identifier, value):
        this = Container()
        
        variables = [v for v in vars(this) if v[0] != '_']
        plate = Container._db.getOne("plates", variables, [identifier + "=" + str(value)])
        
        if plate is not None:
            for v in variables:
                setattr(this, v, getattr(plate, v) )
        else:
            print 'Not found'
            
        return this

    def store(self, fields = None):
        if fields is None:
            fields = [v for v in vars(self) if v[0] != '_']
            
        row = {v : getattr(self,v) for v in fields}    
                
        if self.id == 0:
            fulllist = Container._db.getAll("plates", ['id'])
            
            if fulllist is not None:
                max_id = max([x.id for x in fulllist])
            else:
                max_id = 0
            self.id = max_id + 1
                    
        Container._db.insert('plates', row)
        Container._db.commit()
        
        
    @staticmethod
    def from_id(general_id):
        return Container._from('general_id', "'" + general_id + "'")

    @staticmethod
    def from_index(idx):
        return Container._from('id', idx)

    @staticmethod
    def from_name(name):
        return Container._from('general_name', "'" + name + "'")
        
if __name__ == '__main__':
    c = Container(well_size_x = 2.0, well_shape='round', well_bottom_shape='bubble', well_depth = -3)
        
#    print 'Well area : ' + str(c.wellarea) + " mm2"
#    print 'Safe pipetting depth : ' + str(c.well_depth_safe()) + " mm"
#    print 'Total volume : ' + str(c.well_volume_at_depth(3.0)) + " ul"
#    print 'Dead volume : ' +str(c.well_dead_volume()) + " ul"
#    print str(c.well_surface_at_depth(c.well_depth - c._headheight())) + " mm2"
    
#    print str(c.height_by_volume(100))    
    
#    print c._headvolume(c._headheight())
    xv = np.arange(0,c.well_depth,0.01)
    yv = [ c.well_volume_at_depth(x) for x in xv]
    
    c._construct()
    
#    print c.gen_str
#    print c.gen_str_prop
    
    #print c._gen_knockoutvars()

#    print c._gen_html_query('')
#    print c._gen_mysql_createtable('plates')

