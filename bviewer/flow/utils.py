# -*- coding: utf-8 -*-


class FlowImage(object):
    def __init__(self, entity):
        self.id = entity.id
        self.entity = entity
        self.width = entity.exif.width
        self.height = entity.exif.height
        self.vertical = self.height > self.width

    def width_for(self, height):
        scale = height / float(self.height)
        return int(self.width * scale)

    def update_size(self, height):
        self.width = self.width_for(height)
        self.height = height

    def __repr__(self):
        return 'FlowImage({id}, {w}, {h})' \
            .format(id=self.id, w=self.width, h=self.height)


class FlowRow(object):
    def __init__(self, flow):
        """
        :type flow: FlowCollection
        """
        self.flow = flow
        self.images = []

    def add(self, image):
        width = self.flow.width_sum(self.flow_height, self.images)
        if width < self.flow.flow_width or len(self.images) < 3:
            self.images.append(image)
            return True
        return False

    @property
    def flow_height(self):
        """
        If more than 1 vertical image, make height * 1.2
        """
        if len([i for i in self.images if i.vertical]) > 1:
            return int(self.flow.flow_height * 1.2)
        return self.flow.flow_height

    def scale_size(self, row):
        height = self.flow_height
        while self.flow.width_sum(height, row) > self.flow.flow_width:
            height -= 1
        for image in row:
            image.update_size(height)
        return row

    def has_items(self):
        return bool(self.images)

    def __iter__(self):
        return iter(self.scale_size(self.images))

    def __repr__(self):
        args = ', '.join(str(i) for i in self.scale_size(self.images))
        return 'FlowRow[{0}]'.format(args)


class FlowCollection(object):
    def __init__(self, flow_width, flow_height, margin):
        self.flow_width = flow_width
        self.flow_height = flow_height
        self.margin = margin
        self.images = []
        self._rows = []

    def add(self, images):
        self.images = [FlowImage(i) for i in images]
        self.split_for_rows()

    def split_for_rows(self):
        row = FlowRow(self)
        for image in self.images:
            if not row.add(image):
                self._rows.append(row)
                row = FlowRow(self)
                row.add(image)
        if row.has_items():
            self._rows.append(row)

    def width_sum(self, height, row):
        return sum(i.width_for(height) + self.margin for i in row)

    def __iter__(self):
        for row in self._rows:
            for image in row:
                yield image

    def __repr__(self):
        return 'FlowCollection[{0}]'.format(list(self))
