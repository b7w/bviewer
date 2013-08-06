# -*- coding: utf-8 -*-
from mock import Mock

from django.test import TestCase

from bviewer.flow.controllers import FlowImage, FlowRow


class FlowImageTest(TestCase):
    def test_flow_image(self):
        entity = Mock(id='id1', exif=Mock(width=900, height=600))
        image1 = FlowImage(entity)
        entity = Mock(id='id2', exif=Mock(width=600, height=900))
        image2 = FlowImage(entity)

        self.assertFalse(image1.vertical)
        self.assertTrue(image2.vertical)

        self.assertEqual(image1.width_for(200), 300)
        image1.update_size(200)
        self.assertEqual(image1.height, 200)
        self.assertEqual(image1.width, 300)

        self.assertEqual(image2.width_for(300), 200)
        image2.update_size(300)
        self.assertEqual(image2.height, 300)
        self.assertEqual(image2.width, 200)


class FlowRowTest(TestCase):
    def test_flow_row_add(self):
        row = FlowRow(flow=Mock(flow_width=1000))
        image = Mock(vertical=False)

        row.width_sum = lambda f, s: 600
        self.assertTrue(row.add(image))

        row.width_sum = lambda f, s: 1200
        self.assertTrue(row.add(image))
        self.assertTrue(row.add(image))

        self.assertFalse(row.add(image))

    def test_flow_row_height(self):
        row = FlowRow(flow=Mock(flow_height=100))

        row.images = [Mock(vertical=True), Mock(vertical=False), Mock(vertical=False)]
        self.assertEqual(row.flow_height, 100)

        row.images = [Mock(vertical=True), Mock(vertical=True), Mock(vertical=False)]
        self.assertEqual(row.flow_height, 120)

    def test_flow_row_has_items(self):
        row = FlowRow(flow=Mock())
        row.images = []
        self.assertFalse(row.has_items())
        row.images = [Mock()]
        self.assertTrue(row.has_items())

    def test_flow_scale_size(self):
        entity = Mock(id='id1', exif=Mock(width=600, height=300))
        image1 = FlowImage(entity)
        image2 = FlowImage(entity)
        image3 = FlowImage(entity)
        images = [image1, image2, image3]

        flow = Mock(flow_width=1200, flow_height=400, margin=0)
        row = FlowRow(flow)

        width_sum = sum(i.width for i in row.scale_size(images))
        self.assertEqual(width_sum, 1200)
        self.assertEqual(image1.height, 200)
        self.assertEqual(image2.height, 200)
        self.assertEqual(image3.height, 200)


class FlowControllerTest(TestCase):
    def test_flow_image(self):
        pass