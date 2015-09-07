# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import logging

from math import ceil

import flask
from api.models import ModelList


available_per_page = [10, 20, 50]


def get_pagination_params():
    try:
        page = int(flask.request.args.get('page', 1))
        per_page = int(flask.request.args.get('per_page', available_per_page[0]))
        per_page = per_page if per_page in available_per_page else available_per_page[0]
        return page, per_page
    except Exception as e:
        logging.warn('Unable to get pagination params, error: {0}'.format(e))
        return 0, available_per_page[0]


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @classmethod
    def create_from_model_list(cls, model):
        """
        :type model: ModelList
        :rtype: Pagination
        """
        page, per_page = get_pagination_params()
        return cls(page, per_page, model.total)

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            show_on_left = num <= left_edge
            show_on_right = num > self.pages - right_edge
            show_in_middle = self.page - left_current - 1 < num < self.page + right_current
            if show_on_left or show_in_middle or show_on_right:
                if last + 1 != num:
                    yield None
                yield num
                last = num
