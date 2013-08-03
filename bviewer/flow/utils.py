# -*- coding: utf-8 -*-


class FlowImage(object):
    def __init__(self, entity, width, height):
        self.id = entity.id
        self.entity = entity
        self.width = width
        self.height = height

    def width_for(self, height):
        scale = height / float(self.height)
        return int(self.width * scale)

    def update(self, height):
        self.width = self.width_for(height)
        self.height = height

    def __repr__(self):
        return 'FlowImage({id}, {w},{h})' \
            .format(id=self.id, w=self.width, h=self.height)


class FlowRow(object):
    def __init__(self, flow):
        """
        :type flow: FlowCollection
        """
        self.flow = flow
        self.row = []

    def add(self, image, width, height):
        if self.flow.check_sum(height, self.row) < self.flow.flow_width:
            self.row.append(FlowImage(image, width, height))
            return True
        return False


class FlowCollection(object):
    def __init__(self, flow_width, flow_height, margin):
        self.flow_width = flow_width
        self.flow_height = flow_height
        self.margin = margin
        self.rows = []
        self.buf = []

    def add(self, image, width, height):
        self.buf.append(FlowImage(image, width, height))
        if self.check_sum(self.flow_height, self.buf) > self.flow_width:
            self.rows.append(tuple(self.buf))
            self.buf = []

    def check_sum(self, height, row):
        return sum(i.width_for(height) + self.margin for i in row)

    def optimise_row_height(self, row):
        height = self.flow_height
        while self.check_sum(height, row) > self.flow_width:
            height -= 1
        for image in row:
            image.update(height)
        return row

    def __iter__(self):
        for row in self.rows:
            for image in self.optimise_row_height(row):
                yield image