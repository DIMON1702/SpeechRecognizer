json = require "/usr/share/freeswitch/scripts/json"

function Call_Python(session_uid,speech,confirm)
	-- Вызов .py скрипта
	local pt_request = py_call .. session_uid .. ' "' .. speech ..'" ' .. confirm
	freeswitch.consoleLog("CRIT", pt_request .. "\n")
	local handle = io.popen(pt_request)
	local con_result = handle:read("*a")
	handle:close()
	con_result = con_result:gsub("'", '"')
	freeswitch.consoleLog("CRIT", session_uid .. " PT ANSWER: " .. con_result .. "\n")
	return json.decode(con_result)
end

function onInput(s, type, obj)
	if (type == "event") then			
		local event = obj:getHeader("Speech-Type")		
		if (event == "detected-partial-speech") then
			if (obj:getBody()) then
				pr_speech = obj:getBody()			
				if (pr_speech ~= "") then
					freeswitch.consoleLog("INFO", uid .. " partial: " .. pr_speech .. "\n")
					speech=pr_speech
					return false
				end
			end        
		end
		if (event == "detected-speech") then
			if (obj:getBody()) then
				pr_speech = obj:getBody()					
				if (pr_speech ~= "") then
					freeswitch.consoleLog("CRIT", uid .. " FINAL: " .. pr_speech .. "\n")
					speech=pr_speech
					return false
				end
			end
		end
	end
	return false;
end

py_call = 'python3 /usr/share/freeswitch/scripts/make_request.py ' -- скрипт обработки запросов
record_dir = '/usr/share/freeswitch/scripts/records/' -- директория сохранения полных записей разговора
orig_path = argv[1] -- переданный параметром путь originate
speech = ''
timeout = 0 
session1=freeswitch.Session(orig_path)
if (session1:ready()) then
	uid=session1:getVariable("uuid")
	curr_wait_time = 0
	while (session1:ready() and not session1:answered()) do
		if curr_wait_time > 15000 then return end -- длительность неответа мс
		freeswitch.consoleLog("INFO", uid .. " waiting for answer ...\n")
		session1:sleep(500);
		curr_wait_time = curr_wait_time + 500
	end
	if (session1:ready()) then
		freeswitch.consoleLog("INFO", uid .. " STARTING CALL \n")
		session1:sleep(1500) -- нужна пауза для того чтобы подключились медиа после дозвона
		session1:setInputCallback("onInput")
		session1:execute("record_session", record_dir .. uid .. '.wav')
		result = Call_Python(uid,'none','confirm'); -- Первый вызов
	end
	while (session1:ready()) do
		for i,v in ipairs(result) do
			if v.action == "speak" then
				-- Что-то говорим клиенту
				session1:streamFile(v.data)
			elseif v.action == "transfer" then
				-- Переводим звонок на оператора
				session2 = freeswitch.Session(v.data, session1)
				if (session2:ready()) then
					freeswitch.bridge(session1, session2)
				end;
				-- разсоединяем абонентов после того как они поговорили
				if (session2:ready()) then 
					session2:hangup()
				end
				if (session1:ready()) then 
					session1:hangup()
				end
			elseif v.action == "disconnect" then
				session1:hangup()
			end
		end
		if timeout<36 then -- Если таймаут больше 6 то мы не выключали распознавание
			speech = ''
			session1:execute("detect_speech", "vosk default default")
		end
		result={}
		timeout=0 -- отрезки по 0,2 секунды
		speech_timeout = 0
		accepted_speech = '' 
		while (session1:ready()) do
			timeout=timeout+1
			if (timeout>35 and speech_timeout>15) then
				result = Call_Python(uid,'answer_timeout','confirm')
				break
			end
			if (speech ~= "") then
				temp_speech=speech
				speech=''
				speech_timeout = 0
				temp_result = Call_Python(uid,temp_speech,'none')			 
				if next(temp_result) then
					accepted_speech=temp_speech
					result = temp_result
				end
			end
			session1:sleep(200)
			speech_timeout = speech_timeout + 1
			if (speech_timeout>2 and next(result))then
				freeswitch.consoleLog("CRIT", uid .. " SPEECH TIMEOUT DO STEP\n")
				Call_Python(uid,accepted_speech,'confirm')
				session1:execute("detect_speech", "stop")
				timeout=0
				break				
			end
		end
	end
end