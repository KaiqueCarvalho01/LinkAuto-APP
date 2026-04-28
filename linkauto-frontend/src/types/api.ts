export interface ApiErrorDetail {
	code: string;
	message: string;
}

export interface ApiSuccessEnvelope<TData> {
	data: TData;
	error: null;
	meta: Record<string, unknown>;
}

export interface ApiErrorEnvelope {
	data: null;
	error: ApiErrorDetail;
	meta: Record<string, unknown>;
}
