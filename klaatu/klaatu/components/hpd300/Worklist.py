"""
Created on 26.09.2014

@author: Jan-Hendrik Prinz
"""

from lxml import etree, objectify

from klaatu.util.xmlutil.XMLFactory import XMLFactory
# from klaatu.util.xmlutil.XMLInspect import XMLInspector


class D300Worklist(object):
    """
    Simple Class to construct a D300 Dispense .DATA.xml file from simple building blocks

    Attributes
    ----------
    fluid : XMLFactory
        Construct a fluid block that contains details about a fluid
    dmso : XMLFactory
        Construct a dmso block that contains details about a fluid that is used for normalization
    cassette : XMLFactory
        Construct a cassette block that contains details about a cassette. This only contains 'T4' or 'T8' type
    plate : XMLFactory
        Construct a plate block that contains details about a plate like, 96 or 384, etc...
    head : XMLFactory
        Construct a dispensehead block that contains details about the usage of a dispensehead
    container : XMLFactory
        Construct a plate block for a container for the pipetting steps
    dispense : XMLFactory
        Construct a dispense block that contains details about amounts to be dispensed


    ToDo
    ----
    - Add more convenience functions
    - Add functions to use with EVO pipetting class
    """

    def __init__(self):
        fac = XMLFactory

        template = objectify.parse('template.DATA.xml')
        self.all = fac.from_xml(template)

        # Get template XML factories for fluid, plate, cassette and fluid dispenses, etc.

        self.fluid = fac.from_xml(template.xpath('/Report/Fluids/Fluid')[0])
        self.dmso = fac.from_xml(template.xpath('/Report/Fluids/Fluid')[1])
        self.cassette = fac.from_xml(template.xpath('/Report/Cassettes/Cassette')[0])
        self.plate = fac.from_xml(template.xpath('/Report/Plates/Plate')[0])
        self.head = fac.from_xml(template.xpath('/Report/DispenseHeads/DispenseHead')[0])

        self.container = fac.from_xml(template.xpath('/Report/Dispensed/Plate')[0])
        self.well = fac.from_xml(template.xpath('/Report/Dispensed/Plate/Well')[0])
        self.dispense = fac.from_xml(template.xpath('/Report/Dispensed/Plate/Well/Fluid')[0])


wl = D300Worklist()

result = wl.all(
    fluids=[
        wl.fluid(index=0, name='Bosutinib'),
        wl.fluid(index=1, name='DMSO')
    ],
    plates=[
        wl.plate()
    ],
    cassettes=[wl.cassette()],
    dispense_heads=[
        wl.head(cassette=0, head=0, fluid=0),
        wl.head(cassette=0, head=0, fluid=1)
    ],
    dispensed=[wl.container(
        index=no,
        plate=[
            wl.well(
                r=row, c=col,
                well=[
                    wl.dispense(
                        index=0, cassette=0, head=0, volume=20, total_volume=20
                    ),
                    wl.dispense(
                        index=1, cassette=0, head=1, volume=200, total_volume=200
                    )]
            )
            for row in range(0, 8)
            for col in range(0, 12)
        ]

    )
    for no in range(0, 2)
    ]
)

print etree.tostring(result, pretty_print=True)

from PIL import Image
im = Image.open("Christmas-Tree.png")
pix = im.load()
for y in range(im.size[0]):
    for x in range(im.size[1]):
        r = pix[y,x][0]
        g = pix[y,x][1]
        a = pix[y,x][3]

        c =  (255.0 - r) * a / 255.0 / 255.0
        volume = 1.0;

        vr = - c / (c - 1) * volume

        print vr,

#        print r * a / 255,

        # Red actually removes green and blue
        # Green removes red and blue


    print ""