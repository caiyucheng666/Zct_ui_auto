// 职策佳平台 UI 自动化 —— Jenkins 流水线（Windows）
// 每天早上 09:30 全量跑测试 -> 生成 Allure 报告 -> 邮件通知
// 测试账号不经 .env 文件写入，直接由 Jenkins 凭据以环境变量注入，
// config.py 会优先读系统/进程环境变量（utils/config.py:_load_dotenv 仅在环境变量未设置时兜底 .env）。
pipeline {
    agent any

    triggers {
        // 每天 09:30 触发一次
        cron('30 9 * * *')
    }

    // 路径可在这里改：不要依赖服务环境的 PATH（Jenkins 以 Windows 服务运行时读不到用户 PATH，
    // 且系统里有 Store 版 python 别名会挡路），显式写全路径最稳。
    parameters {
        string(name: 'PYTHON',
               defaultValue: 'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe',
               description: '基础 Python 解释器，用于创建 venv')
        string(name: 'ALLURE',
               defaultValue: 'D:\\allure-2.24.1\\bin\\allure.bat',
               description: 'allure 命令行可执行文件')
    }

    options {
        timestamps()                     // 日志加时间戳（需 Timestamper 插件）
        disableConcurrentBuilds()        // 同一时间只跑一个构建
        timeout(time: 120, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '10'))
    }

    stages {
        stage('拉取代码') {
            steps {
                checkout scm
            }
        }

        stage('准备环境') {
            steps {
                // 若通过 /build 直接触发（不带参数），PYTHON 会是空串，这里兜底用默认路径
                script {
                    env.PYTHON = params.PYTHON ?: 'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python311\\python.exe'
                }
                bat '''
                if not exist .venv\\Scripts\\python.exe "%PYTHON%" -m venv .venv
                .venv\\Scripts\\python.exe -m pip install -r requirements.txt -q --disable-pip-version-check
                '''
            }
        }

        stage('运行测试') {
            steps {
                // 测试账号从 Jenkins 凭据注入环境变量（zct-phone / zct-password）
                // catchError：即使有用例失败（pytest 返回非 0），也让流水线继续跑到 Allure 阶段，
                // 保证失败时也能生成报告；最终构建结果仍记为 FAILURE，触发失败邮件。
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    withCredentials([
                        string(credentialsId: 'zct-phone', variable: 'ZCT_PHONE'),
                        string(credentialsId: 'zct-password', variable: 'ZCT_PASSWORD')
                    ]) {
                        bat '''
                        if not exist reports mkdir reports
                        .venv\\Scripts\\python.exe -m pytest --junitxml=./reports/junit.xml
                        '''
                    }
                }
            }
        }

        stage('生成 Allure 报告') {
            steps {
                script {
                    env.ALLURE = params.ALLURE ?: 'D:\\allure-2.24.1\\bin\\allure.bat'
                }
                bat '"%ALLURE%" generate ./temps -o ./reports --clean'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
        }
        success {
            emailext(
                to: '2556096448@qq.com',
                from: '2556096448@qq.com',
                replyTo: '2556096448@qq.com',
                subject: "[自动化测试] 通过 ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                mimeType: 'text/html',
                body: """<h3>职策佳平台 UI 自动化测试 —— 通过</h3>
                         <p>构建编号：#${env.BUILD_NUMBER}</p>
                         <p>测试结果：<b style="color:green">成功</b></p>
                         <p>查看 Allure 报告：<a href="${env.BUILD_URL}artifact/reports/index.html">点击这里</a></p>"""
            )
        }
        failure {
            emailext(
                to: '2556096448@qq.com',
                from: '2556096448@qq.com',
                replyTo: '2556096448@qq.com',
                subject: "[自动化测试] 失败 ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                mimeType: 'text/html',
                body: """<h3>职策佳平台 UI 自动化测试 —— 失败</h3>
                         <p>构建编号：#${env.BUILD_NUMBER}</p>
                         <p>测试结果：<b style="color:red">失败</b></p>
                         <p>查看 Allure 报告：<a href="${env.BUILD_URL}artifact/reports/index.html">点击这里</a></p>"""
            )
        }
    }
}
