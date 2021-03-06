from flask import current_app as app
from flask_restful import Resource, abort, reqparse
from flasgger import swag_from
from mongoengine.errors import NotUniqueError, ValidationError
from werkzeug.exceptions import BadRequest, NotFound

from models import Measurement, User, Report
from utils import get_formatted_date, get_today_date, normalize_data


class MeasurementDetail(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sys', type=int, required=False, location='json')
        self.reqparse.add_argument('dia', type=int, required=False, location='json')
        self.reqparse.add_argument('pul', type=int, required=False, location='json')
        super(MeasurementDetail, self).__init__()

    @swag_from('docs/measurement_detail.yml', methods=['GET'])
    def get(self, id):
        # import pdb; pdb.set_trace()
        try:
            measurement = Measurement.objects(id=id).first()
            if measurement is not None:
                return measurement.to_dict(), 200
            abort(404, message=f'Measurement ID ={id} was not found')
        except NotFound as e:
            app.logger.error(e)
            raise e
        except Exception as e:
            app.logger.error(e)
            abort(500, message=str(e))

    @swag_from('docs/measurement_detail.yml', methods=['PATCH'])
    def patch(self, id):
        try:
            measurement = Measurement.objects(id=id).first()
            if measurement is not None:
                if get_formatted_date(measurement.created) != get_formatted_date(get_today_date()):
                    raise BadRequest(f'Cannot update a measurement for {get_formatted_date(measurement.created)}')

                data = self.reqparse.parse_args()
                data = normalize_data(data)
                measurement.update(**data)
                measurement.reload()
                return measurement.to_dict(), 200
            abort(404, message=f'Measurement ID={id} was not found')
        except BadRequest as e:
            app.logger.error(e)
            raise e
        except NotFound as e:
            app.logger.error(e)
            raise e
        except Exception as e:
            app.logger.error(e)
            abort(500, message=str(e))


class MeasurementList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('sys', type=int, required=True, location='json')
        self.reqparse.add_argument('dia', type=int, required=True, location='json')
        self.reqparse.add_argument('pul', type=int, required=True, location='json')
        super(MeasurementList, self).__init__()

    @swag_from('docs/measurement_list.yml', methods=['GET'])
    def get(self):
        try:
            data = [measurement.to_dict() for measurement in Measurement.objects]
            return data, 200
        except Exception as e:
            app.logger.error(e)
            abort(500, message=str(e))

    @swag_from('docs/measurement_list.yml', methods=['POST'])
    def post(self):
        try:
            data = self.reqparse.parse_args()
            measurement = Measurement(**data)
            user = User.objects(email='mauricio@example.com').first()
            measurement.user = user
            measurement.save()
            return measurement.to_dict(), 201
        except BadRequest as e:
            app.logger.error(e)
            abort(400, message=e.data.get('message'))
        except (NotUniqueError, ValidationError) as e:
            app.logger.error(e)
            abort(400, message=str(e))
        except Exception as e:
            app.logger.error(e)
            abort(500, message=str(e))


class ReportDetail(Resource):

    @swag_from('docs/report_detail.yml', methods=['GET'])
    def get(self, period):
        try:
            report = Report.objects(period=period).first()
            if report is not None:
                return report.to_dict(), 200
            abort(404, message=f'Report for period {period} was not found')
        except NotFound as e:
            app.logger.error(e)
            raise e
        except Exception as e:
            app.logger.error(e)
            abort(500, message=str(e))
