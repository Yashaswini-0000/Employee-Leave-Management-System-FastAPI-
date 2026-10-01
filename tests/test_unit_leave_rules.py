from datetime import date
def weekday_count(a,b):
    n=0
    while a<=b:
        n += a.weekday()<5
        from datetime import timedelta
        a += timedelta(days=1)
    return n

def test_weekend_excluded():
    assert weekday_count(date(2026,10,2), date(2026,10,5)) == 2
