package com.intel.analytics.bigdl.ppml.example.vfl_gboost_regression

import com.intel.analytics.bigdl.ppml.FLContext
import com.intel.analytics.bigdl.ppml.algorithms.hfl.LogisticRegression
import com.intel.analytics.bigdl.ppml.algorithms.vfl.FGBoostRegression
import com.intel.analytics.bigdl.ppml.example.DebugLogger
import scopt.OptionParser


// TODO: handle dataset
object VflGBoostRegression extends DebugLogger {

  def getData(dataPath: String, rowKeyName: String, batchSize: Int = 4) = {
    val spark = FLContext.getSparkSession()
    import spark.implicits._
    val df = spark.read.csv(dataPath)

    (df, df)
  }

  def main(args: Array[String]): Unit = {
    case class Params(dataPath: String = null,
                      rowKeyName: String = "ID",
                      learningRate: Float = 0.005f)
    val parser: OptionParser[Params] = new OptionParser[Params]("VFL FGBoost Regression") {
      opt[String]('d', "dataPath")
        .text("data path to load")
        .action((x, params) => params.copy(dataPath = x))
        .required()
      opt[String]('r', "rowKeyName")
        .text("row key name of data")
        .action((x, params) => params.copy(rowKeyName = x))
      opt[String]('l', "learningRate")
        .text("learning rate of training")
        .action((x, params) => params.copy(learningRate = x.toFloat))
    }
    val argv = parser.parse(args, Params()).head
    // load args and get data
    val dataPath = argv.dataPath
    val rowKeyName = argv.rowKeyName
    val learningRate = argv.learningRate


    /**
     * Usage of BigDL PPML starts from here
     */
    FLContext.initFLContext()
    val (trainData, testData) = getData(dataPath, rowKeyName)

    // create LogisticRegression object to train the model
    val fGBoostRegression = new FGBoostRegression()
    fGBoostRegression.fit(trainData, valData = testData)
    fGBoostRegression.evaluate()
    fGBoostRegression.predict(testData)
  }
}
