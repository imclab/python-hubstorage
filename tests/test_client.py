"""
Test Client
"""
import time
from hstestcase import HSTestCase
from hubstorage.utils import millitime


class ClientTest(HSTestCase):

    def test_push_job(self):
        c = self.hsclient
        job = c.push_job(self.projectid, self.spidername,
                        state='running',
                        priority=self.project.jobq.PRIO_LOW,
                        foo='baz')
        m = job.metadata
        self.assertEqual(m.get('state'), u'running', c.auth)
        self.assertEqual(m.get('foo'), u'baz')
        self.project.jobq.delete(job)
        m.expire()
        self.assertEqual(m.get('state'), u'deleted')
        self.assertEqual(m.get('foo'), u'baz')

    def test_botgroup(self):
        self.project.settings.update(botgroups=['foo'], created=millitime())
        self.project.settings.save()
        c = self.hsclient
        q1 = c.push_job(self.project.projectid, self.spidername)
        j1 = c.start_job()
        self.assertEqual(j1, None, 'got %s, pushed job was %s' % (j1, q1))
        j2 = c.start_job(botgroup='bar')
        self.assertEqual(j2, None, 'got %s, pushed job was %s' % (j2, q1))
        j3 = c.start_job(botgroup='foo')
        self.assertEqual(j3.key, q1.key)

    def test_start_job(self):
        job = self.hsclient.start_job(botgroups=self.testbotgroups)
        self.assertEqual(job, None)
        jp = self.hsclient.push_job(self.projectid, self.spidername)
        self.assertEqual(jp.metadata.get('state'), 'pending')
        time.sleep(1)  # give time to process jobq
        jr = self.hsclient.start_job(botgroups=self.testbotgroups)
        self.assertEqual(jr.metadata.get('state'), 'running')
