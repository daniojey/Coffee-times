from rest_framework.throttling import UserRateThrottle


class TrottleProducts(UserRateThrottle):
    rate= '1000/hour'