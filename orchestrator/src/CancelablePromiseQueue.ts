/* eslint-disable @typescript-eslint/no-explicit-any */
import async, { AsyncQueue } from 'async';

class CancelablePromiseQueue {
    private queue: AsyncQueue<{ promiseFactory: () => Promise<any>, callback: (error: any, result: any) => void }>;
    private currentJob: { cancel: () => void } | null;
    private timeoutId: NodeJS.Timeout | null;
    private timeoutCallback: (() => void) | null;

    constructor() {
        // Initializes the queue with a concurrency of 1, ensuring that only one job is processed at a time.
        this.queue = async.queue(async (task, done) => {
            try {
                const result = await this.runJob(task.promiseFactory);
                done(result);
            } catch (error) {
                done(error as Error);
            }
        }, 1);
        this.currentJob = null;
        this.timeoutId = null;
        this.timeoutCallback = null;
    }

    public add(promiseFactory: () => Promise<any>, timeoutCallback?: () => void) {
        if (this.currentJob) {
            this.currentJob.cancel();
        }

        this.timeoutCallback = timeoutCallback || null;
        const jobPromise = this.createCancelablePromise(promiseFactory);
        this.queue.push({ promiseFactory: jobPromise.promiseFactory, callback: jobPromise.callback });

        this.currentJob = jobPromise;
        this.startTimeoutNotification();
    }

    private createCancelablePromise(promiseFactory: () => Promise<any>) {
        let cancel: () => void;
        const promise = new Promise<any>((resolve, reject) => {
            const actualPromise = promiseFactory();
            actualPromise.then((value) => {
                this.clearTimeoutNotification();
                resolve(value);
            }).catch((error) => {
                this.clearTimeoutNotification();
                reject(error);
            });
            cancel = () => reject(new Error('Promise was cancelled'));
        });

        const callback = (error: any, result: any) => {
            if (error) {
                console.error(`Job failed with error: ${error.message}`);
            } else {
                console.log(`Job completed with result: ${result}`);
            }
        };

        return { promiseFactory: () => promise, cancel: cancel!, callback };
    }

    private async runJob(promiseFactory: () => Promise<any>) {
        return await promiseFactory();
    }

    private startTimeoutNotification() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }

        this.timeoutId = setTimeout(() => {
            console.log('Notification: Job is taking longer than 200 seconds');
            if (this.timeoutCallback) {
                this.timeoutCallback();
            }
        }, 200000);
    }

    private clearTimeoutNotification() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }
    }
}

export default CancelablePromiseQueue;
